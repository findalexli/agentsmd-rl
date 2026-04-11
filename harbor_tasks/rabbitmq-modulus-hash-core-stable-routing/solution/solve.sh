#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rabbitmq-server

# Idempotent: skip if already applied
if [ -f deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl ]; then
    echo "Patch already applied."
    exit 0
fi

# 1. Create the new core exchange module with stable routing
cat > deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl <<'ERLANG'
%% This Source Code Form is subject to the terms of the Mozilla Public
%% License, v. 2.0. If a copy of the MPL was not distributed with this
%% file, You can obtain one at https://mozilla.org/MPL/2.0/.
%%
%% Copyright (c) 2007-2026 Broadcom. All Rights Reserved. The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries. All rights reserved.
%%

-module(rabbit_exchange_type_modulus_hash).

-behaviour(rabbit_exchange_type).

-include_lib("rabbit_common/include/rabbit.hrl").

-export([description/0,
         route/3,
         serialise_events/0,
         info/1,
         info/2,
         validate/1,
         validate_binding/2,
         create/2,
         delete/2,
         policy_changed/2,
         add_binding/3,
         remove_bindings/3,
         assert_args_equivalence/2]).

-rabbit_boot_step({?MODULE,
                   [{description, "exchange type x-modulus-hash"},
                    {mfa, {rabbit_registry, register,
                           [exchange, <<"x-modulus-hash">>, ?MODULE]}},
                    {requires, rabbit_registry},
                    {enables, kernel_ready}]}).

%% 2^27
-define(PHASH2_RANGE, 134217728).

description() ->
    [{description, <<"Modulus Hashing Exchange">>}].

route(#exchange{name = Name}, Msg, _Options) ->
    Destinations = rabbit_router:match_routing_key(Name, ['_']),
    case length(Destinations) of
        0 ->
            [];
        Len ->
            %% We sort to guarantee stable routing after node restarts.
            DestinationsSorted = lists:sort(Destinations),
            Hash = erlang:phash2(mc:routing_keys(Msg), ?PHASH2_RANGE),
            Destination = lists:nth(Hash rem Len + 1, DestinationsSorted),
            [Destination]
    end.

info(_) -> [].
info(_, _) -> [].
serialise_events() -> false.
validate(_X) -> ok.
validate_binding(_X, _B) -> ok.
create(_Serial, _X) -> ok.
delete(_Serial, _X) -> ok.
policy_changed(_X1, _X2) -> ok.
add_binding(_Serial, _X, _B) -> ok.
remove_bindings(_Serial, _X, _Bs) -> ok.
assert_args_equivalence(X, Args) ->
    rabbit_exchange:assert_args_equivalence(X, Args).
ERLANG

# 2. Remove the old sharding plugin module
rm -f deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl

# 3. Update the Makefile to include the new test suite
sed -i 's/^PARALLEL_CT_SET_5_D = rabbit_fifo_dlx_integration publisher_confirms_parallel$/PARALLEL_CT_SET_5_D = rabbit_fifo_dlx_integration publisher_confirms_parallel rabbit_exchange_type_modulus_hash/' deps/rabbit/Makefile

# 4. Update the sharding README to reflect that x-modulus-hash is now built-in
cat > /tmp/readme_patch.py <<'PYTHON'
import re

readme_path = "deps/rabbitmq_sharding/README.md"
with open(readme_path, "r") as f:
    content = f.read()

# Replace the old "all or nothing" + "plugin provides" paragraphs
old_section = """The exchanges that ship by default with RabbitMQ work in an "all or
nothing" fashion, i.e: if a routing key matches a set of queues bound
to the exchange, then RabbitMQ will route the message to all the
queues in that set. For this plugin to work it is necessary to
route messages to an exchange that would partition messages, so they
are routed to _at most_ one queue (a subset).

The plugin provides a new exchange type, `"x-modulus-hash"`, that will use
a hashing function to partition messages routed to a logical queue
across a number of regular queues (shards)."""

new_section = """RabbitMQ provides a built-in exchange type, `"x-modulus-hash"`, that will use
a hashing function to partition messages routed to a logical queue
across a number of regular queues (shards). This exchange type is available
in core RabbitMQ and does not require enabling this plugin to be used."""

content = content.replace(old_section, new_section)

# Add the stable routing paragraph after the "binding key" paragraph
binding_key_end = '**This exchange will completely ignore the\nbinding key used to bind the queue to the exchange**.'
stable_routing_para = """

This exchange guarantees stable routing. As long as the bindings to the exchange remain the same,
messages with the same routing key will always be routed to exactly the same destination queue,
even across node restarts."""

if stable_routing_para.strip() not in content:
    content = content.replace(binding_key_end, binding_key_end + stable_routing_para)

with open(readme_path, "w") as f:
    f.write(content)
PYTHON

python3 /tmp/readme_patch.py
rm -f /tmp/readme_patch.py

# 5. Remove the old sharding test suite
rm -f deps/rabbitmq_sharding/test/rabbit_hash_exchange_SUITE.erl

echo "Patch applied successfully."
