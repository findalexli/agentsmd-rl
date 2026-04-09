#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for PR #17212 by directly updating the files

# Create the updated Broker.cs
cat > dotnet/src/webdriver/BiDi/Broker.cs << 'EOF'
// <copyright file="Broker.cs" company="Selenium Committers">
// Licensed to the Software Freedom Conservancy (SFC) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The SFC licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.
// </copyright>

using System.Collections.Concurrent;
using System.Text.Json;
using System.Text.Json.Serialization.Metadata;
using OpenQA.Selenium.BiDi.Session;
using OpenQA.Selenium.Internal.Logging;

namespace OpenQA.Selenium.BiDi;

internal sealed class Broker : IAsyncDisposable
{
    private readonly ILogger _logger = Internal.Logging.Log.GetLogger<Broker>();

    private readonly ITransport _transport;
    private readonly EventDispatcher _eventDispatcher;
    private readonly IBiDi _bidi;

    private readonly ConcurrentDictionary<long, CommandInfo> _pendingCommands = new();

    private long _currentCommandId;

    private readonly Task _receivingMessageTask;
    private readonly CancellationTokenSource _receiveMessagesCancellationTokenSource;

    public Broker(ITransport transport, IBiDi bidi, Func<ISessionModule> sessionProvider)
    {
        _transport = transport;
        _bidi = bidi;
        _eventDispatcher = new EventDispatcher(sessionProvider);

        _receiveMessagesCancellationTokenSource = new CancellationTokenSource();
        _receivingMessageTask = Task.Run(() => ReceiveMessagesAsync(_receiveMessagesCancellationTokenSource.Token));
    }

    public Task<Subscription> SubscribeAsync<TEventArgs>(string eventName, EventHandler eventHandler, SubscriptionOptions? options, JsonTypeInfo<TEventArgs> jsonTypeInfo, CancellationToken cancellationToken)
        where TEventArgs : EventArgs
    {
        return _eventDispatcher.SubscribeAsync(eventName, eventHandler, options, jsonTypeInfo, cancellationToken);
    }

    public async Task<TResult> ExecuteCommandAsync<TCommand, TResult>(TCommand command, CommandOptions? options, JsonTypeInfo<TCommand> jsonCommandTypeInfo, JsonTypeInfo<TResult> jsonResultTypeInfo, CancellationToken cancellationToken)
        where TCommand : Command
        where TResult : EmptyResult
    {
        command.Id = Interlocked.Increment(ref _currentCommandId);

        var tcs = new TaskCompletionSource<EmptyResult>(TaskCreationOptions.RunContinuationsAsynchronously);

        using var cts = cancellationToken.CanBeCanceled
            ? CancellationTokenSource.CreateLinkedTokenSource(cancellationToken)
            : new CancellationTokenSource();

        var timeout = options?.Timeout ?? TimeSpan.FromSeconds(30);
        cts.CancelAfter(timeout);

        var data = JsonSerializer.SerializeToUtf8Bytes(command, jsonCommandTypeInfo);
        var commandInfo = new CommandInfo(tcs, jsonResultTypeInfo);
        _pendingCommands[command.Id] = commandInfo;

        using var ctsRegistration = cts.Token.Register(() =>
        {
            tcs.TrySetCanceled(cts.Token);
            _pendingCommands.TryRemove(command.Id, out _);
        });

        try
        {
            await _transport.SendAsync(data, cts.Token).ConfigureAwait(false);
        }
        catch
        {
            _pendingCommands.TryRemove(command.Id, out _);
            throw;
        }

        return (TResult)await tcs.Task.ConfigureAwait(false);
    }

    public async ValueTask DisposeAsync()
    {
        _receiveMessagesCancellationTokenSource.Cancel();

        await _eventDispatcher.DisposeAsync().ConfigureAwait(false);

        try
        {
            await _receivingMessageTask.ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (_receiveMessagesCancellationTokenSource.IsCancellationRequested)
        {
            // Expected when cancellation is requested, ignore.
        }

        _receiveMessagesCancellationTokenSource.Dispose();

        await _transport.DisposeAsync().ConfigureAwait(false);

        GC.SuppressFinalize(this);
    }

    private void ProcessReceivedMessage(byte[] data)
    {
        const int TypeSuccess = 1;
        const int TypeEvent = 2;
        const int TypeError = 3;

        long? id = default;
        int messageType = 0;
        string? method = default;
        string? error = default;
        string? message = default;
        Utf8JsonReader resultReader = default;
        Utf8JsonReader paramsReader = default;

        Utf8JsonReader reader = new(data);
        reader.Read(); // "{"

        reader.Read();

        while (reader.TokenType == JsonTokenType.PropertyName)
        {
            if (reader.ValueTextEquals("id"u8))
            {
                reader.Read();
                id = reader.GetInt64();
            }
            else if (reader.ValueTextEquals("type"u8))
            {
                reader.Read();
                if (reader.ValueTextEquals("success"u8)) messageType = TypeSuccess;
                else if (reader.ValueTextEquals("event"u8)) messageType = TypeEvent;
                else if (reader.ValueTextEquals("error"u8)) messageType = TypeError;
            }
            else if (reader.ValueTextEquals("method"u8))
            {
                reader.Read();
                method = reader.GetString();
            }
            else if (reader.ValueTextEquals("result"u8))
            {
                reader.Read();
                resultReader = reader; // snapshot
            }
            else if (reader.ValueTextEquals("params"u8))
            {
                reader.Read();
                paramsReader = reader; // snapshot
            }
            else if (reader.ValueTextEquals("error"u8))
            {
                reader.Read();
                error = reader.GetString();
            }
            else if (reader.ValueTextEquals("message"u8))
            {
                reader.Read();
                message = reader.GetString();
            }
            else
            {
                reader.Read();
            }

            reader.Skip();
            reader.Read();
        }

        switch (messageType)
        {
            case TypeSuccess:
                if (id is null) throw new BiDiException("The remote end responded with 'success' message type, but missed required 'id' property.");

                if (_pendingCommands.TryGetValue(id.Value, out var command))
                {
                    try
                    {
                        var commandResult = JsonSerializer.Deserialize(ref resultReader, command.JsonResultTypeInfo)
                            ?? throw new BiDiException("Remote end returned null command result in the 'result' property.");

                        command.TaskCompletionSource.TrySetResult((EmptyResult)commandResult);
                    }
                    catch (Exception ex)
                    {
                        command.TaskCompletionSource.TrySetException(ex);
                    }
                    finally
                    {
                        _pendingCommands.TryRemove(id.Value, out _);
                    }
                }
                else
                {
                    if (_logger.IsEnabled(LogEventLevel.Warn))
                    {
                        _logger.Warn($"The remote end responded with 'success' message type, but no pending command with id {id} was found. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
                    }
                }

                break;

            case TypeEvent:
                if (method is null) throw new BiDiException($"The remote end responded with 'event' message type, but missed required 'method' property. Message content: {System.Text.Encoding.UTF8.GetString(data)}");

                if (!_eventDispatcher.TryGetJsonTypeInfo(method, out var jsonTypeInfo))
                {
                    if (_logger.IsEnabled(LogEventLevel.Warn))
                    {
                        _logger.Warn($"Received BiDi event with method '{method}', but no event type mapping was found. Event will be ignored. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
                    }

                    break;
                }

                var eventArgs = JsonSerializer.Deserialize(ref paramsReader, jsonTypeInfo) as EventArgs
                    ?? throw new BiDiException("Remote end returned null event args in the 'params' property.");

                eventArgs.BiDi = _bidi;

                _eventDispatcher.EnqueueEvent(method, eventArgs);
                break;

            case TypeError:
                if (id is null) throw new BiDiException($"The remote end responded with 'error' message type, but missed required 'id' property. Message content: {System.Text.Encoding.UTF8.GetString(data)}");

                if (_pendingCommands.TryGetValue(id.Value, out var errorCommand))
                {
                    errorCommand.TaskCompletionSource.TrySetException(new BiDiException($"{error}: {message}"));
                    _pendingCommands.TryRemove(id.Value, out _);
                }
                else
                {
                    if (_logger.IsEnabled(LogEventLevel.Warn))
                    {
                        _logger.Warn($"The remote end responded with 'error' message type, but no pending command with id {id} was found. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
                    }
                }

                break;

            default:
                if (_logger.IsEnabled(LogEventLevel.Warn))
                {
                    _logger.Warn($"The remote end responded with unknown message type. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
                }

                break;
        }
    }

    private async Task ReceiveMessagesAsync(CancellationToken cancellationToken)
    {
        try
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                var data = await _transport.ReceiveAsync(cancellationToken).ConfigureAwait(false);

                try
                {
                    ProcessReceivedMessage(data);
                }
                catch (Exception ex)
                {
                    if (_logger.IsEnabled(LogEventLevel.Error))
                    {
                        _logger.Error($"Unhandled error occurred while processing remote message: {ex}");
                    }
                }
            }
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            if (_logger.IsEnabled(LogEventLevel.Error))
            {
                _logger.Error($"Unhandled error occurred while receiving remote messages: {ex}");
            }

            // Fail all pending commands, as the connection is likely broken if we failed to receive messages.
            foreach (var id in _pendingCommands.Keys)
            {
                if (_pendingCommands.TryRemove(id, out var pendingCommand))
                {
                    pendingCommand.TaskCompletionSource.TrySetException(ex);
                }
            }

            throw;
        }
    }

    private readonly record struct CommandInfo(TaskCompletionSource<EmptyResult> TaskCompletionSource, JsonTypeInfo JsonResultTypeInfo);
}
EOF

# Create the updated EventDispatcher.cs
cat > dotnet/src/webdriver/BiDi/EventDispatcher.cs << 'EOF'
// <copyright file="EventDispatcher.cs" company="Selenium Committers">
// Licensed to the Software Freedom Conservancy (SFC) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The SFC licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.
// </copyright>

using System.Collections.Concurrent;
using System.Diagnostics.CodeAnalysis;
using System.Text.Json.Serialization.Metadata;
using System.Threading.Channels;
using OpenQA.Selenium.BiDi.Session;
using OpenQA.Selenium.Internal.Logging;

namespace OpenQA.Selenium.BiDi;

internal sealed class EventDispatcher : IAsyncDisposable
{
    private readonly ILogger _logger = Internal.Logging.Log.GetLogger<EventDispatcher>();

    private readonly Func<ISessionModule> _sessionProvider;

    private readonly ConcurrentDictionary<string, EventRegistration> _eventRegistrations = new();

    private readonly Channel<PendingEvent> _pendingEvents = Channel.CreateUnbounded<PendingEvent>(new()
    {
        SingleReader = true,
        SingleWriter = true
    });

    private readonly Task _eventEmitterTask;

    public EventDispatcher(Func<ISessionModule> sessionProvider)
    {
        _sessionProvider = sessionProvider;
        _eventEmitterTask = Task.Run(ProcessEventsAwaiterAsync);
    }

    public async Task<Subscription> SubscribeAsync<TEventArgs>(string eventName, EventHandler eventHandler, SubscriptionOptions? options, JsonTypeInfo<TEventArgs> jsonTypeInfo, CancellationToken cancellationToken)
        where TEventArgs : EventArgs
    {
        var registration = _eventRegistrations.GetOrAdd(eventName, _ => new EventRegistration(jsonTypeInfo));

        var subscribeResult = await _sessionProvider().SubscribeAsync([eventName], new() { Contexts = options?.Contexts, UserContexts = options?.UserContexts }, cancellationToken).ConfigureAwait(false);

        registration.AddHandler(eventHandler);

        return new Subscription(subscribeResult.Subscription, this, eventHandler);
    }

    public async ValueTask UnsubscribeAsync(Subscription subscription, CancellationToken cancellationToken)
    {
        if (_eventRegistrations.TryGetValue(subscription.EventHandler.EventName, out var registration))
        {
            await _sessionProvider().UnsubscribeAsync([subscription.SubscriptionId], null, cancellationToken).ConfigureAwait(false);
            registration.RemoveHandler(subscription.EventHandler);
        }
    }

    public void EnqueueEvent(string method, EventArgs eventArgs)
    {
        _pendingEvents.Writer.TryWrite(new PendingEvent(method, eventArgs));
    }

    private async Task ProcessEventsAwaiterAsync()
    {
        var reader = _pendingEvents.Reader;
        while (await reader.WaitToReadAsync().ConfigureAwait(false))
        {
            while (reader.TryRead(out var result))
            {
                try
                {
                    if (_eventRegistrations.TryGetValue(result.Method, out var registration))
                    {
                        foreach (var handler in registration.GetHandlers()) // copy-on-write array, safe to iterate
                        {
                            await handler.InvokeAsync(result.EventArgs).ConfigureAwait(false);
                        }
                    }
                }
                catch (Exception ex)
                {
                    if (_logger.IsEnabled(LogEventLevel.Error))
                    {
                        _logger.Error($"Unhandled error processing BiDi event handler: {ex}");
                    }
                }
            }
        }
    }

    public async ValueTask DisposeAsync()
    {
        _pendingEvents.Writer.Complete();

        await _eventEmitterTask.ConfigureAwait(false);

        GC.SuppressFinalize(this);
    }

    public bool TryGetJsonTypeInfo(string eventName, [NotNullWhen(true)] out JsonTypeInfo? jsonTypeInfo)
    {
        if (_eventRegistrations.TryGetValue(eventName, out var registration))
        {
            jsonTypeInfo = registration.TypeInfo;
            return true;
        }

        jsonTypeInfo = null;
        return false;
    }

    private readonly record struct PendingEvent(string Method, EventArgs EventArgs);

    private sealed class EventRegistration(JsonTypeInfo typeInfo)
    {
        private readonly object _lock = new();
        private volatile EventHandler[] _handlers = [];

        public JsonTypeInfo TypeInfo { get; } = typeInfo;

        public EventHandler[] GetHandlers() => _handlers;

        public void AddHandler(EventHandler handler)
        {
            lock (_lock) _handlers = [.. _handlers, handler];
        }

        public void RemoveHandler(EventHandler handler)
        {
            lock (_lock) _handlers = Array.FindAll(_handlers, h => h != handler);
        }
    }
}
EOF

echo "Files updated successfully"

# Verify the distinctive line exists (idempotency check)
if grep -q "TryGetJsonTypeInfo" dotnet/src/webdriver/BiDi/EventDispatcher.cs; then
    echo "Fix verified: TryGetJsonTypeInfo method exists"
else
    echo "Fix verification failed: TryGetJsonTypeInfo method not found"
    exit 1
fi
