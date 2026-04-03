#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tuist

# Idempotent: skip if already applied
if grep -q 'TransportPromExPlugin' tuist_common/lib/tuist_common/http/transport_prom_ex_plugin.ex 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Create tuist_common/lib/tuist_common/http/transport.ex ---
mkdir -p tuist_common/lib/tuist_common/http

cat > tuist_common/lib/tuist_common/http/transport.ex <<'ELIXIR'
defmodule TuistCommon.HTTP.Transport do
  @moduledoc """
  Shared normalization for Bandit and Thousand Island transport telemetry.

  This module intentionally follows the native telemetry contracts exposed by Bandit and
  Thousand Island instead of re-emitting app-specific events.

  Useful upstream references:

  - Bandit telemetry event docs:
    https://github.com/mtrudel/bandit/blob/main/lib/bandit/telemetry.ex
  - Bandit request pipeline, which forwards `error.message` into `[:bandit, :request, ...]`
    telemetry metadata:
    https://github.com/mtrudel/bandit/blob/main/lib/bandit/pipeline.ex
  - Bandit HTTP/1 socket handling, including the `"Body read timeout"` error that we classify
    here:
    https://github.com/mtrudel/bandit/blob/main/lib/bandit/http1/socket.ex
  - Thousand Island telemetry event docs:
    https://github.com/mtrudel/thousand_island/blob/main/lib/thousand_island/telemetry.ex
  - Thousand Island socket internals, which emit `:recv_error`, `:send_error`, and
    `:socket_shutdown` events:
    https://github.com/mtrudel/thousand_island/blob/main/lib/thousand_island/socket.ex

  In practice, this module uses Bandit request metadata to:
  - classify body read timeouts
  - classify request failures
  - extract low-cardinality request tags and log fields

  And it uses Thousand Island connection metadata to:
  - classify connection drops
  - normalize recv/send error tags
  - extract connection-level log fields for incident correlation
  """

  def bandit_request_timeout?(metadata) do
    metadata[:error] == "Body read timeout"
  end

  def bandit_request_failure_reason(metadata) do
    conn = metadata[:conn]
    status = conn && Map.get(conn, :status)

    cond do
      is_integer(status) and status >= 500 -> "server_error"
      not is_nil(metadata[:error]) -> "protocol_error"
      true -> nil
    end
  end

  def bandit_request_metadata(metadata) do
    conn = metadata[:conn]

    %{
      method: (conn && conn.method) || "unknown",
      route: (conn && conn.private[:phoenix_route]) || "unknown"
    }
  end

  def bandit_timeout_log_metadata(measurements, metadata) do
    metadata
    |> bandit_request_metadata()
    |> Map.merge(%{
      request_id: bandit_request_id(metadata),
      request_span_context: format_span_context(metadata[:telemetry_span_context]),
      connection_span_context: format_span_context(metadata[:connection_telemetry_span_context]),
      duration_ms: duration_ms(measurements[:duration]),
      req_body_bytes: measurements[:req_body_bytes],
      error: metadata[:error]
    })
    |> compact_metadata()
  end

  def bandit_exception_log_metadata(measurements, metadata) do
    metadata
    |> bandit_request_metadata()
    |> Map.merge(%{
      request_id: bandit_request_id(metadata),
      request_span_context: format_span_context(metadata[:telemetry_span_context]),
      connection_span_context: format_span_context(metadata[:connection_telemetry_span_context]),
      duration_ms: duration_ms(measurements[:duration]),
      kind: metadata[:kind],
      error: format_exception(metadata[:exception])
    })
    |> compact_metadata()
  end

  def thousand_island_connection_drop_reason(metadata) do
    case metadata[:error] do
      nil -> nil
      :timeout -> "timeout"
      :closed -> "closed"
      {:shutdown, _} -> "shutdown"
      _ -> "other"
    end
  end

  def thousand_island_connection_error_metadata(event)
      when event in [:recv_error, :send_error] do
    %{event: Atom.to_string(event)}
  end

  def thousand_island_connection_log_metadata(measurements, metadata) do
    %{
      connection_span_context: format_span_context(metadata[:telemetry_span_context]),
      remote_address: format_remote_address(metadata[:remote_address]),
      remote_port: metadata[:remote_port],
      duration_ms: duration_ms(measurements[:duration]),
      recv_oct: measurements[:recv_oct],
      send_oct: measurements[:send_oct]
    }
    |> compact_metadata()
  end

  def thousand_island_drop_log_metadata(measurements, metadata, reason) do
    measurements
    |> thousand_island_connection_log_metadata(metadata)
    |> Map.merge(%{
      reason: reason,
      error: inspect(metadata[:error])
    })
    |> compact_metadata()
  end

  def thousand_island_error_log_metadata(event, measurements, metadata)
      when event in [:recv_error, :send_error] do
    measurements
    |> thousand_island_connection_log_metadata(metadata)
    |> Map.merge(%{
      event: Atom.to_string(event),
      error: inspect(measurements[:error])
    })
    |> compact_metadata()
  end

  defp bandit_request_id(metadata) do
    conn = metadata[:conn]

    conn
    |> then(fn conn -> if conn, do: Map.get(conn, :resp_headers, []), else: [] end)
    |> header_value("x-request-id")
  end

  defp format_exception(exception) do
    case exception do
      nil -> nil
      %{__exception__: true} = exception -> Exception.message(exception)
      other -> inspect(other)
    end
  end

  defp format_remote_address(nil), do: nil

  defp format_remote_address(remote_address) do
    remote_address
    |> :inet.ntoa()
    |> to_string()
  rescue
    _ -> inspect(remote_address)
  end

  defp format_span_context(nil), do: nil
  defp format_span_context(span_context), do: inspect(span_context)

  defp header_value(headers, key) do
    case List.keyfind(headers, key, 0) do
      {_key, value} -> value
      nil -> nil
    end
  end

  defp duration_ms(nil), do: nil
  defp duration_ms(duration), do: System.convert_time_unit(duration, :native, :millisecond)

  defp compact_metadata(metadata) do
    metadata
    |> Enum.reject(fn {_key, value} -> is_nil(value) end)
    |> Map.new()
  end
end
ELIXIR

# --- 2. Create tuist_common/lib/tuist_common/http/transport_logger.ex ---
cat > tuist_common/lib/tuist_common/http/transport_logger.ex <<'ELIXIR'
defmodule TuistCommon.HTTP.TransportLogger do
  @moduledoc """
  Logs suspicious Bandit and Thousand Island transport events for incident correlation.
  """

  alias TuistCommon.HTTP.Transport

  require Logger

  @events [
    [:bandit, :request, :stop],
    [:bandit, :request, :exception],
    [:thousand_island, :connection, :stop],
    [:thousand_island, :connection, :recv_error],
    [:thousand_island, :connection, :send_error]
  ]

  def attach(handler_suffix \\ :default) do
    case :telemetry.attach_many(
           handler_id(handler_suffix),
           @events,
           &__MODULE__.handle_event/4,
           nil
         ) do
      :ok -> :ok
      {:error, :already_exists} -> :ok
    end
  end

  def detach(handler_suffix \\ :default) do
    :telemetry.detach(handler_id(handler_suffix))
  end

  def handle_event([:bandit, :request, :stop], measurements, metadata, _config) do
    if Transport.bandit_request_timeout?(metadata) do
      Logger.warning(
        "Bandit request body read timed out",
        Map.to_list(Transport.bandit_timeout_log_metadata(measurements, metadata))
      )
    end
  end

  def handle_event([:bandit, :request, :exception], measurements, metadata, _config) do
    Logger.warning(
      "Bandit request raised an exception",
      Map.to_list(Transport.bandit_exception_log_metadata(measurements, metadata))
    )
  end

  def handle_event([:thousand_island, :connection, :stop], measurements, metadata, _config) do
    case Transport.thousand_island_connection_drop_reason(metadata) do
      nil ->
        :ok

      reason ->
        Logger.warning(
          "Thousand Island connection dropped",
          Map.to_list(Transport.thousand_island_drop_log_metadata(measurements, metadata, reason))
        )
    end
  end

  def handle_event([:thousand_island, :connection, event], measurements, metadata, _config)
      when event in [:recv_error, :send_error] do
    Logger.warning(
      "Thousand Island connection #{event}",
      Map.to_list(Transport.thousand_island_error_log_metadata(event, measurements, metadata))
    )
  end

  defp handler_id(handler_suffix), do: "#{__MODULE__}.#{handler_suffix}"
end
ELIXIR

# --- 3. Create tuist_common/lib/tuist_common/http/transport_prom_ex_plugin.ex ---
cat > tuist_common/lib/tuist_common/http/transport_prom_ex_plugin.ex <<'ELIXIR'
defmodule TuistCommon.HTTP.TransportPromExPlugin do
  @moduledoc """
  PromEx transport metrics for Bandit and Thousand Island.

  The current metric set focuses on transport-layer failures and timeouts.
  """
  use PromEx.Plugin

  alias TuistCommon.HTTP.Transport

  @impl true
  def event_metrics(_opts) do
    [
      Event.build(
        :tuist_http_request_timeout_metrics,
        [
          counter(
            [:tuist, :http, :request, :timeout, :count],
            event_name: [:bandit, :request, :stop],
            keep: fn metadata, _measurements -> Transport.bandit_request_timeout?(metadata) end,
            tag_values: &Transport.bandit_request_metadata/1,
            tags: [:method, :route],
            description: "Counts request body read timeouts reported by Bandit."
          )
        ]
      ),
      Event.build(
        :tuist_http_request_failure_metrics,
        [
          counter(
            [:tuist, :http, :request, :failure, :count],
            event_name: [:bandit, :request, :stop],
            keep: fn metadata, _measurements ->
              not is_nil(Transport.bandit_request_failure_reason(metadata))
            end,
            tag_values: &bandit_failure_tag_values/1,
            tags: [:method, :route, :reason],
            description: "Counts failed Bandit requests that indicate unhealthy behavior."
          ),
          counter(
            [:tuist, :http, :request, :failure, :count],
            event_name: [:bandit, :request, :exception],
            tag_values: &bandit_exception_tag_values/1,
            tags: [:method, :route, :reason],
            description: "Counts failed Bandit requests that indicate unhealthy behavior."
          )
        ]
      ),
      Event.build(
        :tuist_http_connection_drop_metrics,
        [
          counter(
            [:tuist, :http, :connection, :drop, :count],
            event_name: [:thousand_island, :connection, :stop],
            keep: fn metadata, _measurements ->
              not is_nil(Transport.thousand_island_connection_drop_reason(metadata))
            end,
            tag_values: fn metadata ->
              %{reason: Transport.thousand_island_connection_drop_reason(metadata)}
            end,
            tags: [:reason],
            description: "Counts Thousand Island connection drops that ended with an error."
          )
        ]
      ),
      Event.build(
        :tuist_http_connection_error_metrics,
        [
          counter(
            [:tuist, :http, :connection, :error, :count],
            event_name: [:thousand_island, :connection, :recv_error],
            tag_values: fn _metadata ->
              Transport.thousand_island_connection_error_metadata(:recv_error)
            end,
            tags: [:event],
            description: "Counts Thousand Island synchronous recv/send errors."
          ),
          counter(
            [:tuist, :http, :connection, :error, :count],
            event_name: [:thousand_island, :connection, :send_error],
            tag_values: fn _metadata ->
              Transport.thousand_island_connection_error_metadata(:send_error)
            end,
            tags: [:event],
            description: "Counts Thousand Island synchronous recv/send errors."
          )
        ]
      )
    ]
  end

  defp bandit_failure_tag_values(metadata) do
    metadata
    |> Transport.bandit_request_metadata()
    |> Map.put(:reason, Transport.bandit_request_failure_reason(metadata))
  end

  defp bandit_exception_tag_values(metadata) do
    Transport.bandit_request_metadata(metadata)
    |> Map.put(:reason, "exception")
  end
end
ELIXIR

# --- 4. Update server/lib/tuist/application.ex ---
# Add alias after existing aliases
sed -i '/alias Tuist.Xcode.XcodeTarget$/a\  alias TuistCommon.HTTP.TransportLogger' server/lib/tuist/application.ex

# Add TransportLogger.attach(:tuist) after ReqTelemetry line
sed -i '/ReqTelemetry.attach_default_logger(:pipeline)$/a\    TransportLogger.attach(:tuist)' server/lib/tuist/application.ex

# --- 5. Update server/lib/tuist/prom_ex.ex ---
# Add TransportPromExPlugin after Tuist.HTTP.PromExPlugin
sed -i 's/        Tuist.HTTP.PromExPlugin$/        Tuist.HTTP.PromExPlugin,\n        TuistCommon.HTTP.TransportPromExPlugin/' server/lib/tuist/prom_ex.ex

# --- 6. Update cache/lib/cache/application.ex ---
# Add alias after existing aliases
sed -i '/alias Cache.DBConnection.TelemetryListener$/a\  alias TuistCommon.HTTP.TransportLogger' cache/lib/cache/application.ex

# Add TransportLogger.attach(:cache) after Oban.Telemetry line
sed -i '/Oban.Telemetry.attach_default_logger()$/a\    TransportLogger.attach(:cache)' cache/lib/cache/application.ex

# --- 7. Update cache/lib/cache/prom_ex.ex ---
# Add TransportPromExPlugin after Cache.Authentication.PromExPlugin
sed -i 's/      Cache.Authentication.PromExPlugin$/      Cache.Authentication.PromExPlugin,\n      TuistCommon.HTTP.TransportPromExPlugin/' cache/lib/cache/prom_ex.ex

# --- 8. Update tuist_common/mix.exs — add prom_ex dependency ---
sed -i '/{:phoenix, "\~> 1.7", only: :test},$/a\      {:prom_ex, git: "https://github.com/pepicrft/prom_ex", branch: "finch"},' tuist_common/mix.exs

# --- 9. Update cache/mix.exs — switch prom_ex to git dep ---
sed -i 's|{:prom_ex, "\~> 1.10"}|{:prom_ex, git: "https://github.com/pepicrft/prom_ex", branch: "finch"}|' cache/mix.exs

# --- 10. Update server/lib/tuist/http/AGENTS.md ---
cat > server/lib/tuist/http/AGENTS.md <<'AGENTSMD'
# Http (Context)

This context defines server-owned HTTP observability integration.

## Responsibilities
- Emit server-owned HTTP client metrics for Finch request lifecycle (queue, connection, send, receive).
- Reuse shared transport observability from `tuist_common/lib/tuist_common/http` for Bandit and Thousand Island server metrics/logging.

## Boundaries
- HTTP/API and UI code live in `server/lib/tuist_web`.
- Configuration belongs in `server/config`.
- Schema changes and migrations live in `server/priv`.
- Shared Bandit/Thousand Island observability belongs in `tuist_common/`.

## Guardrails
- If changes add or modify stored customer data, update `server/data-export.md`.

## Related Context
- Parent business logic: `server/lib/tuist/AGENTS.md`
- Web layer: `server/lib/tuist_web/AGENTS.md`
- Migrations: `server/priv/AGENTS.md`
AGENTSMD

echo "Patch applied successfully."
