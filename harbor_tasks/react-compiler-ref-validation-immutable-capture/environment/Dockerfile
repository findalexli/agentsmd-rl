FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Configure git (needed before any commits)
RUN git config --global user.email "test@example.com" && \
    git config --global user.name "Test User"

# Clone React repo at base commit (pre-fix)
ARG BASE_COMMIT=c0060cf2a695d719152c939cfc3cced8f7da3e52
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Set working directory to compiler
WORKDIR /workspace/react/compiler

# Install dependencies
RUN yarn install --frozen-lockfile

# --- Test infrastructure (NOT the fix) ---
# These changes add the PanResponder fixture and type definitions needed to
# exercise the ImmutableCapture+Freeze validation path. The actual fix is in
# ValidateNoRefAccessInRender.ts, applied separately by solve.sh.

# 1. Create PanResponder fixture file
RUN cat > packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/panresponder-ref-in-callback.js <<'FIXTURE'
// @flow
import {PanResponder, Stringify} from 'shared-runtime';

export default component Playground() {
  const onDragEndRef = useRef(() => {});
  useEffect(() => {
    onDragEndRef.current = () => {
      console.log('drag ended');
    };
  });
  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onPanResponderTerminate: () => {
          onDragEndRef.current();
        },
      }),
    []
  );
  return <Stringify responder={panResponder} />;
}
FIXTURE

# 2. Add PanResponder runtime export
RUN cat >> packages/snap/src/sprout/shared-runtime.ts <<'EOF'

export const PanResponder = {
  create(obj: any): any {
    return obj;
  },
};
EOF

# 3. Add PanResponder type definition to shared-runtime-type-provider
RUN python3 <<'PYEOF'
path = "/workspace/react/compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts"
with open(path) as f:
    content = f.read()

insert_block = """\
          PanResponder: {
            kind: 'object',
            properties: {
              create: {
                kind: 'function',
                positionalParams: [EffectEnum.Freeze],
                restParam: null,
                calleeEffect: EffectEnum.Read,
                returnType: {kind: 'type', name: 'Any'},
                returnValueKind: ValueKindEnum.Frozen,
                aliasing: {
                  receiver: '@receiver',
                  params: ['@config'],
                  rest: null,
                  returns: '@returns',
                  temporaries: [],
                  effects: [
                    {
                      kind: 'Freeze',
                      value: '@config',
                      reason: ValueReasonEnum.KnownReturnSignature,
                    },
                    {
                      kind: 'Create',
                      into: '@returns',
                      value: ValueKindEnum.Frozen,
                      reason: ValueReasonEnum.KnownReturnSignature,
                    },
                    {
                      kind: 'ImmutableCapture',
                      from: '@config',
                      into: '@returns',
                    },
                  ],
                },
              },
            },
          },
"""

marker = "        },\n      };\n    } else if (moduleName === 'ReactCompilerKnownIncompatibleTest')"
replacement = insert_block + "        },\n      };\n    } else if (moduleName === 'ReactCompilerKnownIncompatibleTest')"
assert marker in content, f"Could not find insertion marker in {path}"
content = content.replace(marker, replacement)
with open(path, 'w') as f:
    f.write(content)
print("PanResponder type definition inserted successfully")
PYEOF

# Build snap tool (after source modifications so PanResponder type is included)
RUN yarn workspace snap build

# Commit infrastructure so working tree is clean for the agent
RUN cd /workspace/react && git add -A && git commit -m "test infrastructure"

# Create logs directory
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR /workspace/react
