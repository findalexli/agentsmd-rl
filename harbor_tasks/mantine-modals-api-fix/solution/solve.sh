#!/bin/bash
set -e

# Apply the gold patch to fix the breaking changes in @mantine/modals
# This reverts the API changes introduced in commit ddde2b0

cd /workspace/mantine

# Write context.ts
cat > packages/@mantine/modals/src/context.ts << 'EOF'
import { createContext, ReactNode } from 'react';
import { ModalProps } from '@mantine/core';
import type { ConfirmModalProps } from './ConfirmModal';

export type ModalSettings = Partial<Omit<ModalProps, 'opened'>> & { modalId?: string };

export type ConfirmLabels = Record<'confirm' | 'cancel', ReactNode>;

export interface OpenConfirmModal extends ModalSettings, ConfirmModalProps {}
export interface OpenContextModal<CustomProps extends Record<string, any> = {}>
  extends ModalSettings {
  innerProps: CustomProps;
}

export interface ContextModalProps<T extends Record<string, any> = {}> {
  context: ModalsContextProps;
  innerProps: T;
  id: string;
}

export type ModalState =
  | { id: string; props: ModalSettings; type: 'content' }
  | { id: string; props: OpenConfirmModal; type: 'confirm' }
  | { id: string; props: OpenContextModal; type: 'context'; ctx: string };

export interface ModalsContextProps {
  modalProps: ModalSettings;
  modals: ModalState[];
  openModal: (props: ModalSettings) => string;
  openConfirmModal: (props: OpenConfirmModal) => string;
  openContextModal: <TKey extends MantineModal>(
    modal: TKey,
    props: OpenContextModal<Parameters<MantineModals[TKey]>[0]['innerProps']>
  ) => string;
  closeModal: (id: string, canceled?: boolean) => void;
  closeContextModal: <TKey extends MantineModal>(id: TKey, canceled?: boolean) => void;
  closeAll: () => void;
  updateModal: (payload: { modalId: string } & Partial<OpenConfirmModal>) => void;
  updateContextModal: (payload: { modalId: string } & Partial<OpenContextModal<any>>) => void;
}

export interface MantineModalsOverride {}

export type MantineModalsOverwritten = MantineModalsOverride extends {
  modals: Record<string, React.FC<ContextModalProps<any>>>;
}
  ? MantineModalsOverride
  : {
      modals: Record<string, React.FC<ContextModalProps<any>>>;
    };

export type MantineModals = MantineModalsOverwritten['modals'];

export type MantineModal = keyof MantineModals;

export const ModalsContext = createContext<ModalsContextProps>(null as any);
ModalsContext.displayName = '@mantine/modals/ModalsContext';
EOF

# Write events.ts
cat > packages/@mantine/modals/src/events.ts << 'EOF'
import { createUseExternalEvents, DataAttributes } from '@mantine/core';
import { randomId } from '@mantine/hooks';
import {
  MantineModal,
  MantineModals,
  ModalSettings,
  OpenConfirmModal,
  OpenContextModal,
} from './context';

type ModalsEvents = {
  openModal: (payload: ModalSettings) => string;
  openConfirmModal: (payload: OpenConfirmModal) => string;
  openContextModal: <TKey extends MantineModal>(
    payload: OpenContextModal<Parameters<MantineModals[TKey]>[0]['innerProps']> & {
      modal: TKey;
    } & DataAttributes
  ) => string;
  closeModal: (id: string) => void;
  closeContextModal: <TKey extends MantineModal>(id: TKey) => void;
  closeAllModals: () => void;
  updateModal: (
    payload: { modalId: string } & Partial<ModalSettings> & Partial<OpenConfirmModal>
  ) => void;
  updateContextModal: (payload: { modalId: string } & Partial<OpenContextModal<any>>) => void;
};

export const [useModalsEvents, createEvent] =
  createUseExternalEvents<ModalsEvents>('mantine-modals');

export const openModal: ModalsEvents['openModal'] = (payload) => {
  const id = payload.modalId || randomId();
  createEvent('openModal')({ ...payload, modalId: id });
  return id;
};

export const openConfirmModal: ModalsEvents['openConfirmModal'] = (payload) => {
  const id = payload.modalId || randomId();
  createEvent('openConfirmModal')({ ...payload, modalId: id });
  return id;
};

export const openContextModal: ModalsEvents['openContextModal'] = <TKey extends MantineModal>(
  payload: OpenContextModal<Parameters<MantineModals[TKey]>[0]['innerProps']> & {
    modal: TKey;
  } & DataAttributes
) => {
  const id = payload.modalId || randomId();
  createEvent('openContextModal')({ ...payload, modalId: id });
  return id;
};

export const closeModal = createEvent('closeModal');

export const closeContextModal: ModalsEvents['closeContextModal'] = <TKey extends MantineModal>(
  id: TKey
) => createEvent('closeContextModal')(id);

export const closeAllModals = createEvent('closeAllModals');

export const updateModal = (payload: { modalId: string } & Partial<ModalSettings>) =>
  createEvent('updateModal')(payload);

export const updateContextModal = (payload: { modalId: string } & Partial<OpenContextModal<any>>) =>
  createEvent('updateContextModal')(payload);

export const modals: {
  open: ModalsEvents['openModal'];
  close: ModalsEvents['closeModal'];
  closeAll: ModalsEvents['closeAllModals'];
  openConfirmModal: ModalsEvents['openConfirmModal'];
  openContextModal: ModalsEvents['openContextModal'];
  updateModal: ModalsEvents['updateModal'];
  updateContextModal: ModalsEvents['updateContextModal'];
} = {
  open: openModal,
  close: closeModal,
  closeAll: closeAllModals,
  openConfirmModal,
  openContextModal,
  updateModal,
  updateContextModal,
};
EOF

# Write ModalsProvider.tsx
cat > packages/@mantine/modals/src/ModalsProvider.tsx << 'EOF'
import { useCallback, useReducer, useRef } from 'react';
import { getDefaultZIndex, Modal } from '@mantine/core';
import { randomId } from '@mantine/hooks';
import { ConfirmModal } from './ConfirmModal';
import {
  ConfirmLabels,
  ContextModalProps,
  ModalsContext,
  ModalsContextProps,
  ModalSettings,
  OpenConfirmModal,
  OpenContextModal,
} from './context';
import { useModalsEvents } from './events';
import { modalsReducer } from './reducer';

export interface ModalsProviderProps {
  /** Your app */
  children?: React.ReactNode;

  /** Predefined modals */
  modals?: Record<string, React.FC<ContextModalProps<any>>>;

  /** Shared Modal component props, applied for every modal */
  modalProps?: ModalSettings;

  /** Confirm modal labels */
  labels?: ConfirmLabels;
}

function separateConfirmModalProps(props: OpenConfirmModal) {
  if (!props) {
    return { confirmProps: {}, modalProps: {} };
  }

  const {
    id,
    children,
    onCancel,
    onConfirm,
    closeOnConfirm,
    closeOnCancel,
    cancelProps,
    confirmProps,
    groupProps,
    labels,
    ...others
  } = props;

  return {
    confirmProps: {
      id,
      children,
      onCancel,
      onConfirm,
      closeOnConfirm,
      closeOnCancel,
      cancelProps,
      confirmProps,
      groupProps,
      labels,
    },
    modalProps: {
      id,
      ...others,
    },
  };
}

export function ModalsProvider({ children, modalProps, labels, modals }: ModalsProviderProps) {
  const [state, dispatch] = useReducer(modalsReducer, { modals: [], current: null });
  const stateRef = useRef(state);
  stateRef.current = state;

  const closeAll = useCallback(
    (canceled?: boolean) => {
      dispatch({ type: 'CLOSE_ALL', canceled });
    },
    [stateRef, dispatch]
  );

  const openModal = useCallback(
    ({ modalId, ...props }: ModalSettings) => {
      const id = modalId || randomId();

      dispatch({
        type: 'OPEN',
        modal: {
          id,
          type: 'content',
          props,
        },
      });
      return id;
    },
    [dispatch]
  );

  const openConfirmModal = useCallback(
    ({ modalId, ...props }: OpenConfirmModal) => {
      const id = modalId || randomId();
      dispatch({
        type: 'OPEN',
        modal: {
          id,
          type: 'confirm',
          props,
        },
      });
      return id;
    },
    [dispatch]
  );

  const openContextModal = useCallback(
    (modal: string, { modalId, ...props }: OpenContextModal) => {
      const id = modalId || randomId();
      dispatch({
        type: 'OPEN',
        modal: {
          id,
          type: 'context',
          props,
          ctx: modal,
        },
      });
      return id;
    },
    [dispatch]
  );

  const closeModal = useCallback(
    (id: string, canceled?: boolean) => {
      dispatch({ type: 'CLOSE', modalId: id, canceled });
    },
    [stateRef, dispatch]
  );

  const updateModal = useCallback(
    ({ modalId, ...newProps }: Partial<ModalSettings> & { modalId: string }) => {
      dispatch({
        type: 'UPDATE',
        modalId,
        newProps,
      });
    },
    [dispatch]
  );

  const updateContextModal = useCallback(
    ({ modalId, ...newProps }: { modalId: string } & Partial<OpenContextModal<any>>) => {
      dispatch({ type: 'UPDATE', modalId, newProps });
    },
    [dispatch]
  );

  useModalsEvents({
    openModal,
    openConfirmModal,
    openContextModal: ({ modal, ...payload }: any) => openContextModal(modal, payload),
    closeModal,
    closeContextModal: closeModal,
    closeAllModals: closeAll,
    updateModal,
    updateContextModal,
  });

  const ctx: ModalsContextProps = {
    modalProps: modalProps || {},
    modals: state.modals,
    openModal,
    openConfirmModal,
    openContextModal,
    closeModal,
    closeContextModal: closeModal,
    closeAll,
    updateModal,
    updateContextModal,
  };

  const getCurrentModal = () => {
    const currentModal = stateRef.current.current;
    switch (currentModal?.type) {
      case 'context': {
        const { innerProps, ...rest } = currentModal.props;
        const ContextModal = modals![currentModal.ctx];

        return {
          modalProps: rest,
          content: <ContextModal innerProps={innerProps} context={ctx} id={currentModal.id} />,
        };
      }
      case 'confirm': {
        const { modalProps: separatedModalProps, confirmProps: separatedConfirmProps } =
          separateConfirmModalProps(currentModal.props);

        return {
          modalProps: separatedModalProps,
          content: (
            <ConfirmModal
              {...separatedConfirmProps}
              id={currentModal.id}
              labels={currentModal.props.labels || labels}
            />
          ),
        };
      }
      case 'content': {
        const { children: currentModalChildren, ...rest } = currentModal.props;

        return {
          modalProps: rest,
          content: currentModalChildren,
        };
      }
      default: {
        return {
          modalProps: {},
          content: null,
        };
      }
    }
  };

  const { modalProps: currentModalProps, content } = getCurrentModal();

  return (
    <ModalsContext.Provider value={ctx}>
      <Modal
        zIndex={getDefaultZIndex('modal') + 1}
        {...modalProps}
        {...currentModalProps}
        opened={state.modals.length > 0}
        onClose={() => closeModal(state.current?.id as any)}
      >
        {content}
      </Modal>

      {children}
    </ModalsContext.Provider>
  );
}
EOF

# Write index.ts - remove closeContextModal export
cat > packages/@mantine/modals/src/index.ts << 'EOF'
export { ModalsProvider } from './ModalsProvider.js';
export { useModals } from './use-modals/use-modals.js';
export {
  openModal,
  closeModal,
  closeAllModals,
  openConfirmModal,
  openContextModal,
  updateModal,
  updateContextModal,
  modals,
} from './events.js';

export type { ModalsProviderProps } from './ModalsProvider';
export type {
  ContextModalProps,
  MantineModalsOverride,
  MantineModals,
  MantineModal,
} from './context';
export type { ConfirmModalProps } from './ConfirmModal';
EOF

# Fix reducer.ts - update OpenContextModal type reference
sed -i "s/(newProps as Partial<OpenContextModal>).innerProps,/(newProps as Partial<OpenContextModal<any>>).innerProps,/g" packages/@mantine/modals/src/reducer.ts

# Fix use-modals.test.tsx - update test to use two arguments and correct expectations
sed -i "s/modals.openContextModal({$/modals.openContextModal('contextTest', {/g" packages/@mantine/modals/src/use-modals/use-modals.test.tsx
sed -i "s/modalKey: 'contextTest',$/innerProps: { text: testContent },/g" packages/@mantine/modals/src/use-modals/use-modals.test.tsx
sed -i "s/innerProps: { text: testContent },$/transitionProps: { duration: 0 },/g" packages/@mantine/modals/src/use-modals/use-modals.test.tsx
sed -i "/transitionProps: { duration: 0 },/{N;d}" packages/@mantine/modals/src/use-modals/use-modals.test.tsx

# Actually let me fix the test file more carefully
cat > packages/@mantine/modals/src/use-modals/use-modals.test.tsx << 'EOF'
import { PropsWithChildren, useEffect } from 'react';
import { render, renderHook, screen } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { ContextModalProps } from '../context';
import { ModalsProvider } from '../ModalsProvider';
import { useModals } from './use-modals';

describe('@mantine/modals/use-modals', () => {
  it('returns context value of ModalsProvider', () => {
    const wrapper = ({ children }: PropsWithChildren<unknown>) => (
      <MantineProvider>
        <ModalsProvider>{children}</ModalsProvider>
      </MantineProvider>
    );

    const hook = renderHook(() => useModals(), { wrapper });
    const { current } = hook.result;

    expect(current.closeAll).toBeDefined();
    expect(current.closeModal).toBeDefined();
    expect(current.closeContextModal).toBeDefined();
    expect(current.modals).toBeDefined();
    expect(current.openConfirmModal).toBeDefined();
    expect(current.openContextModal).toBeDefined();
    expect(current.openModal).toBeDefined();
  });

  it('correctly passes innerProps to a context modal', () => {
    const ContextModal = ({ innerProps }: ContextModalProps<{ text: string }>) => (
      <div>{innerProps.text}</div>
    );

    const wrapper = ({ children }: any) => (
      <MantineProvider>
        <ModalsProvider modals={{ contextTest: ContextModal }}>{children}</ModalsProvider>
      </MantineProvider>
    );

    const testContent = 'context-modal-test-content';
    const Component = () => {
      const modals = useModals();

      useEffect(() => {
        modals.openContextModal('contextTest', {
          innerProps: { text: testContent },
          transitionProps: { duration: 0 },
        });
      }, []);

      return <div>Empty</div>;
    };

    render(<Component />, { wrapper });
    expect(screen.getByText(testContent)).toBeInTheDocument();
  });

  it('correctly renders a confirm modal with labels from the provider', () => {
    const wrapper = ({ children }: any) => (
      <MantineProvider>
        <ModalsProvider labels={{ cancel: 'ProviderCancel', confirm: 'ProviderConfirm' }}>
          {children}
        </ModalsProvider>
      </MantineProvider>
    );

    const Component = () => {
      const modals = useModals();

      useEffect(() => {
        modals.openConfirmModal({ transitionProps: { duration: 0 } });
      }, []);

      return <div>Empty</div>;
    };

    render(<Component />, { wrapper });
    expect(screen.getByText('ProviderCancel')).toBeInTheDocument();
    expect(screen.getByText('ProviderConfirm')).toBeInTheDocument();
  });

  it('correctly renders a confirm modal with overwritten provider labels', () => {
    const wrapper = ({ children }: any) => (
      <MantineProvider>
        <ModalsProvider labels={{ cancel: 'ProviderCancel', confirm: 'ProviderConfirm' }}>
          {children}
        </ModalsProvider>
      </MantineProvider>
    );

    const Component = () => {
      const modals = useModals();

      useEffect(() => {
        modals.openConfirmModal({
          labels: { confirm: 'Confirm', cancel: 'Cancel' },
          transitionProps: { duration: 0 },
        });
      }, []);

      return <div>Empty</div>;
    };

    render(<Component />, { wrapper });
    expect(screen.getByText('Confirm')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('correctly renders a confirm modal with labels as HTMLElement', () => {
    const wrapper = ({ children }: any) => (
      <MantineProvider>
        <ModalsProvider>{children}</ModalsProvider>
      </MantineProvider>
    );

    const Component = () => {
      const modals = useModals();

      useEffect(() => {
        modals.openConfirmModal({
          labels: {
            confirm: <span>Confirm</span>,
            cancel: <span>Cancel</span>,
          },
          transitionProps: { duration: 0 },
        });
      }, []);

      return <div>Empty</div>;
    };

    render(<Component />, { wrapper });

    expect(screen.getByText('Confirm')).toContainHTML('span');
    expect(screen.getByText('Cancel')).toContainHTML('span');
  });

  it('correctly renders a regular modal with children and a title', () => {
    const wrapper = ({ children }: any) => (
      <MantineProvider>
        <ModalsProvider>{children}</ModalsProvider>
      </MantineProvider>
    );

    const Component = () => {
      const modals = useModals();

      useEffect(() => {
        modals.openModal({
          title: 'Test title',
          children: <h1>Children</h1>,
          transitionProps: { duration: 0 },
        });
      }, []);

      return <div>Empty</div>;
    };

    render(<Component />, { wrapper });
    expect(screen.getByText('Test title')).toBeInTheDocument();
    expect(screen.getByText('Children')).toBeInTheDocument();
  });
});
EOF

# Fix story file - update openContextModal calls
sed -i "s/openContextModal({$/openContextModal('hello', {/g" packages/@mantine/modals/src/Modals.story.tsx
sed -i "s/modalId: 'context-modal',$/modalId: 'context-modal',/g" packages/@mantine/modals/src/Modals.story.tsx
sed -i "/modalId: 'context-modal',/{n;d}" packages/@mantine/modals/src/Modals.story.tsx  # Remove modalKey line
sed -i "s/modals.closeAllModals();/modals.closeAll();/g" packages/@mantine/modals/src/Modals.story.tsx

# Fix the UpdateContextModal part of the story file
# First, let's see what the file looks like
if grep -q "modalKey: 'asyncProcessing'" packages/@mantine/modals/src/Modals.story.tsx; then
    # Replace the problematic section
    sed -i "s/const modalId = modals.openContextModal({$/const modalId = modals.openContextModal('asyncProcessing', {/g" packages/@mantine/modals/src/Modals.story.tsx
    # Remove the next line which should be modalKey
    sed -i "/const modalId = modals.openContextModal('asyncProcessing', {/{n;d}" packages/@mantine/modals/src/Modals.story.tsx
fi

# Fix the updateContextModal call - remove modalKey from it
sed -i '/modals.updateContextModal({/,/})/{/modalKey:/d}' packages/@mantine/modals/src/Modals.story.tsx

# Check if patch was applied successfully
if grep -q "modal: string, { modalId, ...props }" packages/@mantine/modals/src/ModalsProvider.tsx; then
    echo "Patch applied successfully - openContextModal now takes two arguments"
else
    echo "Warning: Patch may not have applied correctly"
    exit 1
fi

echo "Fix applied successfully"
