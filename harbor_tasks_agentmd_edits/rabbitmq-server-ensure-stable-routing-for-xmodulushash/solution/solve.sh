#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rabbitmq-server

# Idempotent: skip if already applied
if [ -f deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl ]; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/deps/rabbit/Makefile b/deps/rabbit/Makefile
index 25512921601d..7b97ba58126c 100644
--- a/deps/rabbit/Makefile
+++ b/deps/rabbit/Makefile
@@ -271,7 +271,7 @@ PARALLEL_CT_SET_4_D = per_user_connection_channel_tracking product_info queue_ty
 PARALLEL_CT_SET_5_A = rabbit_direct_reply_to_prop rabbit_quorum_queue_prop direct_reply_to_amqpl direct_reply_to_amqp classic_queue
 PARALLEL_CT_SET_5_B = feature_flags_v2 backing_queue transactions
 PARALLEL_CT_SET_5_C = cluster_upgrade maintenance_mode
-PARALLEL_CT_SET_5_D = rabbit_fifo_dlx_integration publisher_confirms_parallel
+PARALLEL_CT_SET_5_D = rabbit_fifo_dlx_integration publisher_confirms_parallel rabbit_exchange_type_modulus_hash
 
 PARALLEL_CT_SET_1 = $(sort $(PARALLEL_CT_SET_1_A) $(PARALLEL_CT_SET_1_B) $(PARALLEL_CT_SET_1_C) $(PARALLEL_CT_SET_1_D))
 PARALLEL_CT_SET_2 = $(sort $(PARALLEL_CT_SET_2_A) $(PARALLEL_CT_SET_2_B) $(PARALLEL_CT_SET_2_C) $(PARALLEL_CT_SET_2_D))
diff --git a/deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl b/deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl
new file mode 100644
index 000000000000..31c197dcb0b8
--- /dev/null
+++ b/deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl
@@ -0,0 +1,65 @@
+%% This Source Code Form is subject to the terms of the Mozilla Public
+%% License, v. 2.0. If a copy of the MPL was not distributed with this
+%% file, You can obtain one at https://mozilla.org/MPL/2.0/.
+%%
+%% Copyright (c) 2007-2026 Broadcom. All Rights Reserved. The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries. All rights reserved.
+%%
+
+-module(rabbit_exchange_type_modulus_hash).
+
+-behaviour(rabbit_exchange_type).
+
+-include_lib("rabbit_common/include/rabbit.hrl").
+
+-export([description/0,
+         route/3,
+         serialise_events/0,
+         info/1,
+         info/2,
+         validate/1,
+         validate_binding/2,
+         create/2,
+         delete/2,
+         policy_changed/2,
+         add_binding/3,
+         remove_bindings/3,
+         assert_args_equivalence/2]).
+
+-rabbit_boot_step({?MODULE,
+                   [{description, "exchange type x-modulus-hash"},
+                    {mfa, {rabbit_registry, register,
+                           [exchange, <<"x-modulus-hash">>, ?MODULE]}},
+                    {requires, rabbit_registry},
+                    {enables, kernel_ready}]}).
+
+%% 2^27
+-define(PHASH2_RANGE, 134217728).
+
+description() ->
+    [{description, <<"Modulus Hashing Exchange">>}].
+
+route(#exchange{name = Name}, Msg, _Options) ->
+    Destinations = rabbit_router:match_routing_key(Name, ['_']),
+    case length(Destinations) of
+        0 ->
+            [];
+        Len ->
+            %% We sort to guarantee stable routing after node restarts.
+            DestinationsSorted = lists:sort(Destinations),
+            Hash = erlang:phash2(mc:routing_keys(Msg), ?PHASH2_RANGE),
+            Destination = lists:nth(Hash rem Len + 1, DestinationsSorted),
+            [Destination]
+    end.
+
+info(_) -> [].
+info(_, _) -> [].
+serialise_events() -> false.
+validate(_X) -> ok.
+validate_binding(_X, _B) -> ok.
+create(_Serial, _X) -> ok.
+delete(_Serial, _X) -> ok.
+policy_changed(_X1, _X2) -> ok.
+add_binding(_Serial, _X, _B) -> ok.
+remove_bindings(_Serial, _X, _Bs) -> ok.
+assert_args_equivalence(X, Args) ->
+    rabbit_exchange:assert_args_equivalence(X, Args).
diff --git a/deps/rabbit/test/rabbit_exchange_type_modulus_hash_SUITE.erl b/deps/rabbit/test/rabbit_exchange_type_modulus_hash_SUITE.erl
new file mode 100644
index 000000000000..975a26163194
--- /dev/null
+++ b/deps/rabbit/test/rabbit_exchange_type_modulus_hash_SUITE.erl
@@ -0,0 +1,277 @@
+%% This Source Code Form is subject to the terms of the Mozilla Public
+%% License, v. 2.0. If a copy of the MPL was not distributed with this
+%% file, You can obtain one at https://mozilla.org/MPL/2.0/.
+%%
+%% Copyright (c) 2007-2026 Broadcom. All Rights Reserved. The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries. All rights reserved.
+%%
+-module(rabbit_exchange_type_modulus_hash_SUITE).
+
+-compile(export_all).
+
+-include_lib("amqp_client/include/amqp_client.hrl").
+-include_lib("eunit/include/eunit.hrl").
+
+all() ->
+    [
+     {group, tests}
+    ].
+
+groups() ->
+    [
+     {tests, [],
+      [
+       routed_to_zero_queue_test,
+       routed_to_one_queue_test,
+       routed_to_many_queue_test,
+       stable_routing_across_restarts_test,
+       weighted_routing_test
+      ]}
+    ].
+
+%% -------------------------------------------------------------------
+%% Test suite setup/teardown
+%% -------------------------------------------------------------------
+
+init_per_suite(Config) ->
+    rabbit_ct_helpers:log_environment(),
+    Config1 = rabbit_ct_helpers:set_config(Config, [
+        {rmq_nodename_suffix, ?MODULE}
+      ]),
+    rabbit_ct_helpers:run_setup_steps(Config1,
+      rabbit_ct_broker_helpers:setup_steps() ++
+      rabbit_ct_client_helpers:setup_steps()).
+
+end_per_suite(Config) ->
+    rabbit_ct_helpers:run_teardown_steps(Config,
+      rabbit_ct_client_helpers:teardown_steps() ++
+      rabbit_ct_broker_helpers:teardown_steps()).
+
+init_per_group(_, Config) ->
+    Config.
+
+end_per_group(_, Config) ->
+    Config.
+
+init_per_testcase(Testcase, Config) ->
+    TestCaseName = rabbit_ct_helpers:config_to_testcase_name(Config, Testcase),
+    Config1 = rabbit_ct_helpers:set_config(Config, {test_resource_name,
+                                                    re:replace(TestCaseName, "/", "-", [global, {return, list}])}),
+    rabbit_ct_helpers:testcase_started(Config1, Testcase).
+
+end_per_testcase(Testcase, Config) ->
+    rabbit_ct_helpers:testcase_finished(Config, Testcase).
+
+%% -------------------------------------------------------------------
+%% Test cases
+%% -------------------------------------------------------------------
+
+routed_to_zero_queue_test(Config) ->
+    ok = route(Config, [], 5, 0).
+
+routed_to_one_queue_test(Config) ->
+    ok = route(Config, [<<"q1">>, <<"q2">>, <<"q3">>], 1, 1).
+
+routed_to_many_queue_test(Config) ->
+    ok = route(Config, [<<"q1">>, <<"q2">>, <<"q3">>], 5, 5).
+
+route(Config, Queues, PublishCount, ExpectedRoutedCount) ->
+    {Conn, Chan} = rabbit_ct_client_helpers:open_connection_and_channel(Config),
+    B = rabbit_ct_helpers:get_config(Config, test_resource_name),
+    XNameBin = erlang:list_to_binary("x-" ++ B),
+
+    #'exchange.declare_ok'{} = amqp_channel:call(Chan,
+                                                 #'exchange.declare'{
+                                                    exchange = XNameBin,
+                                                    type = <<"x-modulus-hash">>,
+                                                    durable = true,
+                                                    auto_delete = true}),
+    [begin
+         #'queue.declare_ok'{} = amqp_channel:call(Chan, #'queue.declare'{
+                                                            queue = Q,
+                                                            durable = true,
+                                                            exclusive = true}),
+         #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{
+                                                         queue = Q,
+                                                         exchange = XNameBin})
+     end
+     || Q <- Queues],
+
+    amqp_channel:call(Chan, #'confirm.select'{}),
+    [amqp_channel:call(Chan,
+                       #'basic.publish'{exchange = XNameBin,
+                                        routing_key = rnd()},
+                       #amqp_msg{props = #'P_basic'{},
+                                 payload = <<>>}) ||
+     _ <- lists:duplicate(PublishCount, const)],
+    amqp_channel:wait_for_confirms_or_die(Chan),
+
+    Count = lists:foldl(
+              fun(Q, Acc) ->
+                      #'queue.declare_ok'{message_count = M} = amqp_channel:call(
+                                                                 Chan,
+                                                                 #'queue.declare'{
+                                                                    queue = Q,
+                                                                    durable = true,
+                                                                    exclusive = true}),
+                      Acc + M
+              end, 0, Queues),
+    ?assertEqual(ExpectedRoutedCount, Count),
+
+    amqp_channel:call(Chan, #'exchange.delete'{exchange = XNameBin}),
+    [amqp_channel:call(Chan, #'queue.delete'{queue = Q}) || Q <- Queues],
+    ok = rabbit_ct_client_helpers:close_connection_and_channel(Conn, Chan).
+
+stable_routing_across_restarts_test(Config) ->
+    {Conn1, Chan1} = rabbit_ct_client_helpers:open_connection_and_channel(Config),
+    XNameBin = atom_to_binary(?FUNCTION_NAME),
+    NumQs = 40,
+    NumMsgs = 500,
+
+    #'exchange.declare_ok'{} = amqp_channel:call(Chan1,
+                                                 #'exchange.declare'{
+                                                    exchange = XNameBin,
+                                                    type = <<"x-modulus-hash">>,
+                                                    durable = true}),
+    Queues = [erlang:list_to_binary("q-" ++ integer_to_list(I)) || I <- lists:seq(1, NumQs)],
+    [begin
+         #'queue.declare_ok'{} = amqp_channel:call(Chan1, #'queue.declare'{
+                                                             queue = Q,
+                                                             durable = true}),
+         #'queue.bind_ok'{} = amqp_channel:call(Chan1, #'queue.bind'{
+                                                          queue = Q,
+                                                          exchange = XNameBin,
+                                                          routing_key = rnd()})
+     end
+     || Q <- Queues],
+
+    RoutingKeys = [rnd() || _ <- lists:seq(1, NumMsgs)],
+
+    amqp_channel:call(Chan1, #'confirm.select'{}),
+    [amqp_channel:call(Chan1,
+                       #'basic.publish'{exchange = XNameBin,
+                                        routing_key = RK},
+                       #amqp_msg{payload = RK})
+     || RK <- RoutingKeys],
+    amqp_channel:wait_for_confirms_or_die(Chan1),
+
+    Map1 = consume_all(Chan1, Queues),
+
+    NonEmptyQueues1 = maps:filter(fun(_Q, Msgs) -> length(Msgs) > 0 end, Map1),
+    ?assert(maps:size(NonEmptyQueues1) >= 2),
+
+    ?assertEqual(NumMsgs, lists:sum([length(Msgs) || Msgs <- maps:values(Map1)])),
+
+    ok = rabbit_ct_client_helpers:close_connection_and_channel(Conn1, Chan1),
+    ok = rabbit_ct_broker_helpers:restart_node(Config, 0),
+    {Conn2, Chan2} = rabbit_ct_client_helpers:open_connection_and_channel(Config),
+
+    amqp_channel:call(Chan2, #'confirm.select'{}),
+    [amqp_channel:call(Chan2,
+                       #'basic.publish'{exchange = XNameBin,
+                                        routing_key = RK},
+                       #amqp_msg{payload = RK})
+     || RK <- RoutingKeys],
+    amqp_channel:wait_for_confirms_or_die(Chan2),
+
+    Map2 = consume_all(Chan2, Queues),
+
+    ?assertEqual(Map1, Map2),
+
+    amqp_channel:call(Chan2, #'exchange.delete'{exchange = XNameBin}),
+    [amqp_channel:call(Chan2, #'queue.delete'{queue = Q}) || Q <- Queues],
+    ok = rabbit_ct_client_helpers:close_connection_and_channel(Conn2, Chan2).
+
+weighted_routing_test(Config) ->
+    {Conn, Chan} = rabbit_ct_client_helpers:open_connection_and_channel(Config),
+    XNameBin = atom_to_binary(?FUNCTION_NAME),
+    Queues = [<<"q1">>, <<"q2">>, <<"q3">>],
+    NumMsgs = 600,
+
+    #'exchange.declare_ok'{} = amqp_channel:call(Chan,
+                                                 #'exchange.declare'{
+                                                    exchange = XNameBin,
+                                                    type = <<"x-modulus-hash">>,
+                                                    durable = true}),
+
+    [#'queue.declare_ok'{} = amqp_channel:call(Chan, #'queue.declare'{queue = Q,
+                                                                      durable = true})
+     || Q <- Queues],
+
+    #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{queue = <<"q1">>,
+                                                               exchange = XNameBin}),
+
+    #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{queue = <<"q2">>,
+                                                               exchange = XNameBin,
+                                                               routing_key = <<"a">>}),
+    #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{queue = <<"q2">>,
+                                                               exchange = XNameBin,
+                                                               routing_key = <<"b">>}),
+
+    #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{queue = <<"q3">>,
+                                                               exchange = XNameBin,
+                                                               routing_key = <<"a">>}),
+    #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{queue = <<"q3">>,
+                                                               exchange = XNameBin,
+                                                               routing_key = <<"b">>}),
+    #'queue.bind_ok'{} = amqp_channel:call(Chan, #'queue.bind'{queue = <<"q3">>,
+                                                               exchange = XNameBin,
+                                                               routing_key = <<"c">>}),
+
+    amqp_channel:call(Chan, #'confirm.select'{}),
+    [amqp_channel:call(Chan,
+                       #'basic.publish'{exchange = XNameBin,
+                                        routing_key = integer_to_binary(I)},
+                       #amqp_msg{})
+     || I <- lists:seq(1, NumMsgs)],
+    amqp_channel:wait_for_confirms_or_die(Chan),
+
+    Counts = lists:foldl(
+               fun(Q, Acc) ->
+                       #'queue.declare_ok'{message_count = M} = amqp_channel:call(
+                                                                  Chan,
+                                                                  #'queue.declare'{queue = Q,
+                                                                                   durable = true}),
+                       maps:put(Q, M, Acc)
+               end, #{}, Queues),
+
+    C1 = maps:get(<<"q1">>, Counts),
+    C2 = maps:get(<<"q2">>, Counts),
+    C3 = maps:get(<<"q3">>, Counts),
+    ct:pal("q1: ~b, q2: ~b, q3: ~b", [C1, C2, C3]),
+
+    ?assertEqual(NumMsgs, C1 + C2 + C3),
+    ?assert(C1 < C2),
+    ?assert(C2 < C3),
+
+    amqp_channel:call(Chan, #'exchange.delete'{exchange = XNameBin}),
+    [amqp_channel:call(Chan, #'queue.delete'{queue = Q}) || Q <- Queues],
+    ok = rabbit_ct_client_helpers:close_connection_and_channel(Conn, Chan).
+
+consume_all(Chan, Queues) ->
+    lists:foldl(fun(Q, Map) ->
+                        Msgs = consume_queue(Chan, Q, []),
+                        maps:put(Q, Msgs, Map)
+                end, #{}, Queues).
+
+consume_queue(Chan, Q, L) ->
+    case amqp_channel:call(Chan, #'basic.get'{queue = Q,
+                                              no_ack = true}) of
+        #'basic.get_empty'{} ->
+            L;
+        {#'basic.get_ok'{}, #amqp_msg{payload = Payload}} ->
+            consume_queue(Chan, Q, L ++ [Payload])
+    end.
+
+rnd() ->
+    integer_to_binary(rand:uniform(10_000_000)).
diff --git a/deps/rabbitmq_sharding/README.md b/deps/rabbitmq_sharding/README.md
index bf2fb988cc7d..baf5f40d60b7 100644
--- a/deps/rabbitmq_sharding/README.md
+++ b/deps/rabbitmq_sharding/README.md
@@ -48,16 +48,10 @@ Do not use this plugin with quorum queues. Avoid classic mirrored queues in gene
 
 ## Messages Distribution Between Shards (Partitioning)
 
-The exchanges that ship by default with RabbitMQ work in an "all or
-nothing" fashion, i.e: if a routing key matches a set of queues bound
-to the exchange, then RabbitMQ will route the message to all the
-queues in that set. For this plugin to work it is necessary to
-route messages to an exchange that would partition messages, so they
-are routed to _at most_ one queue (a subset).
-
-The plugin provides a new exchange type, `"x-modulus-hash"`, that will use
+RabbitMQ provides a built-in exchange type, `"x-modulus-hash"`, that will use
 a hashing function to partition messages routed to a logical queue
-across a number of regular queues (shards).
+across a number of regular queues (shards). This exchange type is available
+in core RabbitMQ and does not require enabling this plugin to be used.
 
 The `"x-modulus-hash"` exchange will hash the routing key used to
 publish the message and then it will apply a `Hash mod N` to pick the
@@ -65,6 +59,10 @@ queue where to route the message, where N is the number of queues
 bound to the exchange. **This exchange will completely ignore the
 binding key used to bind the queue to the exchange**.
 
+This exchange guarantees stable routing. As long as the bindings to the exchange remain the same,
+messages with the same routing key will always be routed to exactly the same destination queue,
+even across node restarts.
+
 There are other exchanges with similar behaviour:
 the _Consistent Hash Exchange_ or the _Random Exchange_.
 Those were designed with regular queues in mind, not this plugin, so `"x-modulus-hash"`
diff --git a/deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl b/deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl
deleted file mode 100644
index c94c706379e2..000000000000
--- a/deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl
+++ /dev/null
@@ -1,60 +0,0 @@
-%% This Source Code Form is subject to the terms of the Mozilla Public
-%% License, v. 2.0. If a copy of the MPL was not distributed with this
-%% file, You can obtain one at https://mozilla.org/MPL/2.0/.
-%%
-%% Copyright (c) 2007-2026 Broadcom. All Rights Reserved. The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries. All rights reserved.
-%%
-
--module(rabbit_sharding_exchange_type_modulus_hash).
-
--include_lib("rabbit_common/include/rabbit.hrl").
-
--behaviour(rabbit_exchange_type).
-
--export([description/0, serialise_events/0, route/3, info/1, info/2]).
--export([validate/1, validate_binding/2,
-         create/2, delete/2, policy_changed/2,
-         add_binding/3, remove_bindings/3, assert_args_equivalence/2]).
-
--rabbit_boot_step(
-   {rabbit_sharding_exchange_type_modulus_hash_registry,
-    [{description, "exchange type x-modulus-hash: registry"},
-     {mfa,         {rabbit_registry, register,
-                    [exchange, <<"x-modulus-hash">>, ?MODULE]}},
-     {cleanup, {rabbit_registry, unregister,
-                [exchange, <<"x-modulus-hash">>]}},
-     {requires,    rabbit_registry},
-     {enables,     kernel_ready}]}).
-
--define(PHASH2_RANGE, 134217728). %% 2^27
-
-description() ->
-    [{description, <<"Modulus Hashing Exchange">>}].
-
-serialise_events() -> false.
-
-route(#exchange{name = Name}, Msg, _Options) ->
-    Routes = mc:routing_keys(Msg),
-    Qs = rabbit_router:match_routing_key(Name, ['_']),
-    case length(Qs) of
-        0 -> [];
-        N -> [lists:nth(hash_mod(Routes, N), Qs)]
-    end.
-
-info(_) -> [].
-
-info(_, _) -> [].
-
-validate(_X) -> ok.
-validate_binding(_X, _B) -> ok.
-create(_Serial, _X) -> ok.
-delete(_Serial, _X) -> ok.
-policy_changed(_X1, _X2) -> ok.
-add_binding(_Serial, _X, _B) -> ok.
-remove_bindings(_Serial, _X, _Bs) -> ok.
-assert_args_equivalence(X, Args) ->
-    rabbit_exchange:assert_args_equivalence(X, Args).
-
-hash_mod(Routes, N) ->
-    M = erlang:phash2(Routes, ?PHASH2_RANGE) rem N,
-    M + 1. %% erlang lists are 1..N indexed.
diff --git a/deps/rabbitmq_sharding/test/rabbit_hash_exchange_SUITE.erl b/deps/rabbitmq_sharding/test/rabbit_hash_exchange_SUITE.erl
deleted file mode 100644
index 6991b639fac0..000000000000
--- a/deps/rabbitmq_sharding/test/rabbit_hash_exchange_SUITE.erl
+++ /dev/null
@@ -1,146 +0,0 @@
-%% This Source Code Form is subject to the terms of the Mozilla Public
-%% License, v. 2.0. If a copy of the MPL was not distributed with this
-%% file, You can obtain one at https://mozilla.org/MPL/2.0/.
-%%
-%% Copyright (c) 2007-2026 Broadcom. All Rights Reserved. The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries. All rights reserved.
-%%
--module(rabbit_hash_exchange_SUITE).
-
--compile(export_all).
-
--include_lib("amqp_client/include/amqp_client.hrl").
--include_lib("eunit/include/eunit.hrl").
-
-all() ->
-    [
-      {group, non_parallel_tests}
-    ].
-
-groups() ->
-    [
-      {non_parallel_tests, [], [
-                                routed_to_zero_queue_test,
-                                routed_to_one_queue_test,
-                                routed_to_many_queue_test
-                               ]}
-    ].
-
-%% -------------------------------------------------------------------
-%% Test suite setup/teardown
-%% -------------------------------------------------------------------
-
-init_per_suite(Config) ->
-    rabbit_ct_helpers:log_environment(),
-    Config1 = rabbit_ct_helpers:set_config(Config, [
-        {rmq_nodename_suffix, ?MODULE}
-      ]),
-    rabbit_ct_helpers:run_setup_steps(Config1,
-      rabbit_ct_broker_helpers:setup_steps() ++
-      rabbit_ct_client_helpers:setup_steps()).
-
-end_per_suite(Config) ->
-    rabbit_ct_helpers:run_teardown_steps(Config,
-      rabbit_ct_client_helpers:teardown_steps() ++
-      rabbit_ct_broker_helpers:teardown_steps()).
-
-init_per_group(_, Config) ->
-    Config.
-
-end_per_group(_, Config) ->
-    Config.
-
-init_per_testcase(Testcase, Config) ->
-    TestCaseName = rabbit_ct_helpers:config_to_testcase_name(Config, Testcase),
-    Config1 = rabbit_ct_helpers:set_config(Config, {test_resource_name,
-                                                    re:replace(TestCaseName, "/", "-", [global, {return, list}])}),
-    rabbit_ct_helpers:testcase_started(Config1, Testcase).
-
-end_per_testcase(Testcase, Config) ->
-    rabbit_ct_helpers:testcase_finished(Config, Testcase).
-
-%% -------------------------------------------------------------------
-%% Test cases
-%% -------------------------------------------------------------------
-
-routed_to_zero_queue_test(Config) ->
-    test0(Config, fun () ->
-                  #'basic.publish'{exchange = make_exchange_name(Config, "0"), routing_key = rnd()}
-          end,
-          fun() ->
-                  #amqp_msg{props = #'P_basic'{}, payload = <<>>}
-          end, [], 5, 0),
-
-    passed.
-
-routed_to_one_queue_test(Config) ->
-    test0(Config, fun () ->
-                  #'basic.publish'{exchange = make_exchange_name(Config, "0"), routing_key = rnd()}
-          end,
-          fun() ->
-                  #amqp_msg{props = #'P_basic'{}, payload = <<>>}
-          end, [<<"q1">>, <<"q2">>, <<"q3">>], 1, 1),
-
-    passed.
-
-routed_to_many_queue_test(Config) ->
-    test0(Config, fun () ->
-                  #'basic.publish'{exchange = make_exchange_name(Config, "0"), routing_key = rnd()}
-          end,
-          fun() ->
-                  #amqp_msg{props = #'P_basic'{}, payload = <<>>}
-          end, [<<"q1">>, <<"q2">>, <<"q3">>], 5, 5),
-
-    passed.
-
-test0(Config, MakeMethod, MakeMsg, Queues, MsgCount, Count) ->
-    {Conn, Chan} = rabbit_ct_client_helpers:open_connection_and_channel(Config, 0),
-    E = make_exchange_name(Config, "0"),
-
-    #'exchange.declare_ok'{} =
-        amqp_channel:call(Chan,
-                          #'exchange.declare' {
-                            exchange = E,
-                            type = <<"x-modulus-hash">>,
-                            auto_delete = true
-                           }),
-    [#'queue.declare_ok'{} =
-         amqp_channel:call(Chan, #'queue.declare' {
-                             queue = Q, exclusive = true }) || Q <- Queues],
-    [#'queue.bind_ok'{} =
-         amqp_channel:call(Chan, #'queue.bind'{queue = Q,
-                                               exchange = E,
-                                               routing_key = <<"">>})
-     || Q <- Queues],
-
-    amqp_channel:call(Chan, #'confirm.select'{}),
-
-    [amqp_channel:call(Chan,
-                       MakeMethod(),
-                       MakeMsg()) || _ <- lists:duplicate(MsgCount, const)],
-
-    % ensure that the messages have been delivered to the queues before asking
-    % for the message count
-    amqp_channel:wait_for_confirms_or_die(Chan),
-
-    Counts =
-        [begin
-             #'queue.declare_ok'{message_count = M} =
-                 amqp_channel:call(Chan, #'queue.declare' {queue     = Q,
-                                                           exclusive = true }),
-             M
-         end || Q <- Queues],
-
-    ?assertEqual(Count, lists:sum(Counts)),
-
-    amqp_channel:call(Chan, #'exchange.delete' { exchange = E }),
-    [amqp_channel:call(Chan, #'queue.delete' { queue = Q }) || Q <- Queues],
-
-    rabbit_ct_client_helpers:close_connection_and_channel(Conn, Chan),
-    ok.
-
-rnd() ->
-    list_to_binary(integer_to_list(rand:uniform(1000000))).
-
-make_exchange_name(Config, Suffix) ->
-    B = rabbit_ct_helpers:get_config(Config, test_resource_name),
-    erlang:list_to_binary("x-" ++ B ++ "-" ++ Suffix).

PATCH

echo "Patch applied successfully."
