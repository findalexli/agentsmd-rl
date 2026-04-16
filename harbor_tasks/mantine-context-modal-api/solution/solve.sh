#!/bin/bash
set -e

cd /workspace/mantine

# Apply the gold patch for mantine PR #8439
cat <<'PATCH' | git apply -
diff --git a/packages/@docs/demos/src/demos/modals/Modals.demo.context.tsx b/packages/@docs/demos/src/demos/modals/Modals.demo.context.tsx
index 1111111..2222222 100644
--- a/packages/@docs/demos/src/demos/modals/Modals.demo.context.tsx
+++ b/packages/@docs/demos/src/demos/modals/Modals.demo.context.tsx
@@ -31,7 +31,7 @@ function Demo() {
     <Button
       onClick={() =>
         modals.openContextModal({
-          modal: 'demonstration',
+          modalKey: 'demonstration',
           title: 'Test modal from context',
           innerProps: {
             modalBody:
diff --git a/packages/@docs/demos/src/demos/modals/Modals.demo.updateContextModal.tsx b/packages/@docs/demos/src/demos/modals/Modals.demo.updateContextModal.tsx
index 1111111..2222222 100644
--- a/packages/@docs/demos/src/demos/modals/Modals.demo.updateContextModal.tsx
+++ b/packages/@docs/demos/src/demos/modals/Modals.demo.updateContextModal.tsx
@@ -77,7 +77,7 @@ function Demo() {
     <Button
       onClick={() => {
         const modalId = modals.openContextModal({
-          modal: 'asyncDemonstration',
+          modalKey: 'asyncDemonstration',
           title: 'Processing...',
           closeOnEscape: false,
           closeOnClickOutside: false,
@@ -90,6 +90,7 @@ function Demo() {

         setTimeout(() => {
           modals.updateContextModal({
+            modalKey: 'asyncDemonstration',
             modalId,
             title: 'Processing Complete!',
             closeOnEscape: true,
diff --git a/packages/@mantine/modals/src/Modals.story.tsx b/packages/@mantine/modals/src/Modals.story.tsx
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/Modals.story.tsx
+++ b/packages/@mantine/modals/src/Modals.story.tsx
@@ -27,7 +27,7 @@ export function Usage() {
   const showContextModal = () =>
     openContextModal({
       modalId: 'context-modal',
-      modal: 'hello',
+      modalKey: 'hello',
       title: 'Context modal',
       centered: true,
       onClose: () => console.log('context modal closed'),
@@ -160,7 +160,7 @@ function CloseAllApp() {
       centered: true,
       onClose: () => {
         console.log('Close modal', modalId);
-        modals.closeAll();
+        modals.closeAllModals();
       },
     });
   };
@@ -195,7 +195,8 @@ function UpdateContextModal() {
   const modals = useModals();

   const handleOpenAsyncConfirmModal = () => {
-    const modalId = modals.openContextModal('asyncProcessing', {
+    const modalId = modals.openContextModal({
+      modalKey: 'asyncProcessing',
       title: 'Processing...',
       innerProps: {
         modalBody: 'You cannot close the modal during this operation.',
@@ -209,6 +210,7 @@ function UpdateContextModal() {

     setTimeout(() => {
       modals.updateContextModal({
+        modalKey: 'asyncProcessing',
         modalId,
         title: 'Processing Complete!',
         closeButtonProps: { disabled: false },
diff --git a/packages/@mantine/modals/src/ModalsProvider.tsx b/packages/@mantine/modals/src/ModalsProvider.tsx
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/ModalsProvider.tsx
+++ b/packages/@mantine/modals/src/ModalsProvider.tsx
@@ -4,12 +4,11 @@ import { randomId } from '@mantine/hooks';
 import { ConfirmModal } from './ConfirmModal';
 import {
   ConfirmLabels,
-  ContextModalProps,
+  MantineModals,
   ModalsContext,
   ModalsContextProps,
   ModalSettings,
   OpenConfirmModal,
-  OpenContextModal,
 } from './context';
 import { useModalsEvents } from './events';
 import { modalsReducer } from './reducer';
@@ -19,7 +18,7 @@ export interface ModalsProviderProps {
   children?: React.ReactNode;

   /** Predefined modals */
-  modals?: Record<string, React.FC<ContextModalProps<any>>>;
+  modals?: MantineModals;

   /** Shared Modal component props, applied for every modal */
   modalProps?: ModalSettings;
@@ -72,17 +71,9 @@ export function ModalsProvider({ children, modalProps, labels, modals }: ModalsP
   const stateRef = useRef(state);
   stateRef.current = state;

-  const closeAll = useCallback(
-    (canceled?: boolean) => {
-      dispatch({ type: 'CLOSE_ALL', canceled });
-    },
-    [stateRef, dispatch]
-  );
-
-  const openModal = useCallback(
-    ({ modalId, ...props }: ModalSettings) => {
+  const openModal: ModalsContextProps['openModal'] = useCallback(
+    ({ modalId, ...props }) => {
       const id = modalId || randomId();
-
       dispatch({
         type: 'OPEN',
         modal: {
@@ -96,8 +87,8 @@ export function ModalsProvider({ children, modalProps, labels, modals }: ModalsP
     [dispatch]
   );

-  const openConfirmModal = useCallback(
-    ({ modalId, ...props }: OpenConfirmModal) => {
+  const openConfirmModal: ModalsContextProps['openConfirmModal'] = useCallback(
+    ({ modalId, ...props }) => {
       const id = modalId || randomId();
       dispatch({
         type: 'OPEN',
@@ -112,55 +103,72 @@ export function ModalsProvider({ children, modalProps, labels, modals }: ModalsP
     [dispatch]
   );

-  const openContextModal = useCallback(
-    (modal: string, { modalId, ...props }: OpenContextModal) => {
+  const openContextModal: ModalsContextProps['openContextModal'] = useCallback(
+    ({ modalId, modalKey, ...props }) => {
       const id = modalId || randomId();
       dispatch({
         type: 'OPEN',
         modal: {
           id,
           type: 'context',
           props,
-          ctx: modal,
+          ctx: modalKey,
         },
       });
       return id;
     },
     [dispatch]
   );

-  const closeModal = useCallback(
-    (id: string, canceled?: boolean) => {
+  const closeModal: ModalsContextProps['closeModal'] = useCallback(
+    (modalId: string, canceled?: boolean) => {
+      dispatch({ type: 'CLOSE', modalId, canceled });
+    },
+    [stateRef, dispatch]
+  );
+
+  const closeContextModal: ModalsContextProps['closeContextModal'] = useCallback(
+    (modalKey: string, canceled?: boolean) => {
+      const id =
+        stateRef.current.modals.find((m) => m.type === 'context' && m.ctx === modalKey)?.id ??
+        modalKey;
       dispatch({ type: 'CLOSE', modalId: id, canceled });
     },
     [stateRef, dispatch]
   );

-  const updateModal = useCallback(
-    ({ modalId, ...newProps }: Partial<ModalSettings> & { modalId: string }) => {
-      dispatch({
-        type: 'UPDATE',
-        modalId,
-        newProps,
-      });
+  const closeAllModals: ModalsContextProps['closeAllModals'] = useCallback(
+    (canceled?: boolean) => {
+      dispatch({ type: 'CLOSE_ALL', canceled });
     },
-    [dispatch]
+    [stateRef, dispatch]
   );

-  const updateContextModal = useCallback(
-    ({ modalId, ...newProps }: { modalId: string } & Partial<OpenContextModal<any>>) => {
+  const updateModal: ModalsContextProps['updateModal'] = useCallback(
+    ({ modalId, ...newProps }) => {
       dispatch({ type: 'UPDATE', modalId, newProps });
     },
     [dispatch]
   );

+  const updateContextModal: ModalsContextProps['updateContextModal'] = useCallback(
+    ({ modalKey, modalId, ...newProps }) => {
+      const id =
+        modalId ??
+        stateRef.current.modals.find((m) => m.type === 'context' && m.ctx === modalKey)?.id ??
+        modalKey;
+      dispatch({ type: 'UPDATE', newProps, modalId: id });
+    },
+    [stateRef, dispatch]
+  );
+
   useModalsEvents({
     openModal,
     openConfirmModal,
-    openContextModal: ({ modal, ...payload }: any) => openContextModal(modal, payload),
+    openContextModal,
     closeModal,
-    closeContextModal: closeModal,
-    closeAllModals: closeAll,
+    closeContextModal,
+    closeAllModals,
     updateModal,
     updateContextModal,
   });
@@ -172,8 +180,8 @@ export function ModalsProvider({ children, modalProps, labels, modals }: ModalsP
     openConfirmModal,
     openContextModal,
     closeModal,
-    closeContextModal: closeModal,
-    closeAll,
+    closeContextModal,
+    closeAllModals,
     updateModal,
     updateContextModal,
   };
@@ -231,7 +239,7 @@ export function ModalsProvider({ children, modalProps, labels, modals }: ModalsP
         {...modalProps}
         {...currentModalProps}
         opened={state.modals.length > 0}
-        onClose={() => closeModal(state.current?.id as any)}
+        onClose={() => closeModal(state.current?.id as string)}
       >
         {content}
       </Modal>
diff --git a/packages/@mantine/modals/src/context.ts b/packages/@mantine/modals/src/context.ts
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/context.ts
+++ b/packages/@mantine/modals/src/context.ts
@@ -1,16 +1,20 @@
 import { createContext, ReactNode } from 'react';
-import { ModalProps } from '@mantine/core';
+import { DataAttributes, ModalProps } from '@mantine/core';
 import type { ConfirmModalProps } from './ConfirmModal';

 export type ModalSettings = Partial<Omit<ModalProps, 'opened'>> & { modalId?: string };

 export type ConfirmLabels = Record<'confirm' | 'cancel', ReactNode>;

 export interface OpenConfirmModal extends ModalSettings, ConfirmModalProps {}
-export interface OpenContextModal<CustomProps extends Record<string, any> = {}>
-  extends ModalSettings {
-  innerProps: CustomProps;
-}
+
+export type ContextModalInnerProps<
+  TKey extends MantineModal,
+  P = Parameters<MantineModals[TKey]>[0]['innerProps'],
+> = keyof NonNullable<P> extends never ? { innerProps?: never } : { innerProps: P };
+
+export type OpenContextModal<TKey extends MantineModal = string> = ModalSettings &
+  ContextModalInnerProps<TKey>;

 export interface ContextModalProps<T extends Record<string, any> = {}> {
   context: ModalsContextProps;
@@ -29,27 +33,24 @@ export interface ModalsContextProps {
   openModal: (props: ModalSettings) => string;
   openConfirmModal: (props: OpenConfirmModal) => string;
   openContextModal: <TKey extends MantineModal>(
-    modal: TKey,
-    props: OpenContextModal<Parameters<MantineModals[TKey]>[0]['innerProps']>
+    props: { modalKey: TKey } & OpenContextModal<TKey> & DataAttributes
   ) => string;
-  closeModal: (id: string, canceled?: boolean) => void;
-  closeContextModal: <TKey extends MantineModal>(id: TKey, canceled?: boolean) => void;
-  closeAll: () => void;
-  updateModal: (payload: { modalId: string } & Partial<OpenConfirmModal>) => void;
-  updateContextModal: (payload: { modalId: string } & Partial<OpenContextModal<any>>) => void;
+  closeModal: (modalId: string, canceled?: boolean) => void;
+  closeContextModal: <TKey extends MantineModal>(modalKey: TKey, canceled?: boolean) => void;
+  closeAllModals: () => void;
+  updateModal: (props: { modalId: string } & Partial<OpenConfirmModal>) => void;
+  updateContextModal: <TKey extends MantineModal>(
+    props: { modalKey: TKey } & Partial<OpenContextModal<TKey>>
+  ) => void;
 }

 export interface MantineModalsOverride {}

-export type MantineModalsOverwritten = MantineModalsOverride extends {
-  modals: Record<string, React.FC<ContextModalProps<any>>>;
+export type MantineModals = MantineModalsOverride extends {
+  modals: infer CustomModals;
 }
-  ? MantineModalsOverride
-  : {
-      modals: Record<string, React.FC<ContextModalProps<any>>>;
-    };
-
-export type MantineModals = MantineModalsOverwritten['modals'];
+  ? CustomModals
+  : Record<string, React.FC<ContextModalProps<any>>>;

 export type MantineModal = keyof MantineModals;

 export const ModalsContext = createContext<ModalsContextProps>(null as any);
diff --git a/packages/@mantine/modals/src/events.ts b/packages/@mantine/modals/src/events.ts
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/events.ts
+++ b/packages/@mantine/modals/src/events.ts
@@ -1,29 +1,8 @@
-import { createUseExternalEvents, DataAttributes } from '@mantine/core';
+import { createUseExternalEvents } from '@mantine/core';
 import { randomId } from '@mantine/hooks';
-import {
-  MantineModal,
-  MantineModals,
-  ModalSettings,
-  OpenConfirmModal,
-  OpenContextModal,
-} from './context';
+import { ModalsContextProps } from './context';

-type ModalsEvents = {
-  openModal: (payload: ModalSettings) => string;
-  openConfirmModal: (payload: OpenConfirmModal) => string;
-  openContextModal: <TKey extends MantineModal>(
-    payload: OpenContextModal<Parameters<MantineModals[TKey]>[0]['innerProps']> & {
-      modal: TKey;
-    } & DataAttributes
-  ) => string;
-  closeModal: (id: string) => void;
-  closeContextModal: <TKey extends MantineModal>(id: TKey) => void;
-  closeAllModals: () => void;
-  updateModal: (
-    payload: { modalId: string } & Partial<ModalSettings> & Partial<OpenConfirmModal>
-  ) => void;
-  updateContextModal: (payload: { modalId: string } & Partial<OpenContextModal<any>>) => void;
-};
+type ModalsEvents = Omit<ModalsContextProps, 'modals' | 'modalProps'>;

 export const [useModalsEvents, createEvent] =
   createUseExternalEvents<ModalsEvents>('mantine-modals');
@@ -40,44 +19,41 @@ export const openConfirmModal: ModalsEvents['openConfirmModal'] = (payload) => {
   return id;
 };

-export const openContextModal: ModalsEvents['openContextModal'] = <TKey extends MantineModal>(
-  payload: OpenContextModal<Parameters<MantineModals[TKey]>[0]['innerProps']> & {
-    modal: TKey;
-  } & DataAttributes
-) => {
+export const openContextModal: ModalsEvents['openContextModal'] = (payload) => {
   const id = payload.modalId || randomId();
   createEvent('openContextModal')({ ...payload, modalId: id });
   return id;
 };

-export const closeModal = createEvent('closeModal');
+export const closeModal: ModalsEvents['closeModal'] = createEvent('closeModal');

-export const closeContextModal: ModalsEvents['closeContextModal'] = <TKey extends MantineModal>(
-  id: TKey
-) => createEvent('closeContextModal')(id);
+export const closeContextModal: ModalsEvents['closeContextModal'] = (id) =>
+  createEvent('closeContextModal')(id);

-export const closeAllModals = createEvent('closeAllModals');
+export const closeAllModals: ModalsEvents['closeAllModals'] = createEvent('closeAllModals');

-export const updateModal = (payload: { modalId: string } & Partial<ModalSettings>) =>
+export const updateModal: ModalsEvents['updateModal'] = (payload) =>
   createEvent('updateModal')(payload);

-export const updateContextModal = (payload: { modalId: string } & Partial<OpenContextModal<any>>) =>
+export const updateContextModal: ModalsEvents['updateContextModal'] = (payload) =>
   createEvent('updateContextModal')(payload);

 export const modals: {
   open: ModalsEvents['openModal'];
-  close: ModalsEvents['closeModal'];
-  closeAll: ModalsEvents['closeAllModals'];
   openConfirmModal: ModalsEvents['openConfirmModal'];
   openContextModal: ModalsEvents['openContextModal'];
+  close: ModalsEvents['closeModal'];
+  closeContext: ModalsEvents['closeContextModal'];
+  closeAll: ModalsEvents['closeAllModals'];
   updateModal: ModalsEvents['updateModal'];
   updateContextModal: ModalsEvents['updateContextModal'];
 } = {
   open: openModal,
-  close: closeModal,
-  closeAll: closeAllModals,
   openConfirmModal,
   openContextModal,
+  close: closeModal,
+  closeContext: closeContextModal,
+  closeAll: closeAllModals,
   updateModal,
   updateContextModal,
 };
diff --git a/packages/@mantine/modals/src/index.ts b/packages/@mantine/modals/src/index.ts
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/index.ts
+++ b/packages/@mantine/modals/src/index.ts
@@ -3,6 +3,7 @@ export { useModals } from './use-modals/use-modals.js';
 export {
   openModal,
   closeModal,
+  closeContextModal,
   closeAllModals,
   openConfirmModal,
   openContextModal,
diff --git a/packages/@mantine/modals/src/reducer.ts b/packages/@mantine/modals/src/reducer.ts
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/reducer.ts
+++ b/packages/@mantine/modals/src/reducer.ts
@@ -110,7 +110,7 @@ export function modalsReducer(
               ...newProps,
               innerProps: {
                 ...modal.props.innerProps,
-                ...(newProps as Partial<OpenContextModal<any>>).innerProps,
+                ...(newProps as Partial<OpenContextModal>).innerProps,
               },
             },
           };
diff --git a/packages/@mantine/modals/src/use-modals/use-modals.test.tsx b/packages/@mantine/modals/src/use-modals/use-modals.test.tsx
index 1111111..2222222 100644
--- a/packages/@mantine/modals/src/use-modals/use-modals.test.tsx
+++ b/packages/@mantine/modals/src/use-modals/use-modals.test.tsx
@@ -16,13 +16,15 @@ describe('@mantine/modals/use-modals', () => {
     const hook = renderHook(() => useModals(), { wrapper });
     const { current } = hook.result;

-    expect(current.closeAll).toBeDefined();
-    expect(current.closeModal).toBeDefined();
-    expect(current.closeContextModal).toBeDefined();
     expect(current.modals).toBeDefined();
+    expect(current.openModal).toBeDefined();
     expect(current.openConfirmModal).toBeDefined();
     expect(current.openContextModal).toBeDefined();
-    expect(current.openModal).toBeDefined();
+    expect(current.closeModal).toBeDefined();
+    expect(current.closeAllModals).toBeDefined();
+    expect(current.closeContextModal).toBeDefined();
+    expect(current.updateModal).toBeDefined();
+    expect(current.updateContextModal).toBeDefined();
   });

   it('correctly passes innerProps to a context modal', () => {
@@ -41,7 +43,8 @@ describe('@mantine/modals/use-modals', () => {
       const modals = useModals();

       useEffect(() => {
-        modals.openContextModal('contextTest', {
+        modals.openContextModal({
+          modalKey: 'contextTest',
           innerProps: { text: testContent },
           transitionProps: { duration: 0 },
         });
PATCH

# Verify the patch was applied
grep -q "modalKey:" packages/@mantine/modals/src/context.ts && echo "Patch applied successfully"
