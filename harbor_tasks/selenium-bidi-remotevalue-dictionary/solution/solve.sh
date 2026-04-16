#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check
if grep -q "ConvertRemoteValuesToDictionary" dotnet/src/webdriver/BiDi/Script/RemoteValue.cs 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

python3 << 'PYTHON_SCRIPT'
import re

file_path = "dotnet/src/webdriver/BiDi/Script/RemoteValue.cs"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Add the two new cases after the List conversion case in the switch expression
list_case_pattern = r'(\(ArrayRemoteValue a, Type t\) when t\.IsGenericType && t\.IsAssignableFrom\(typeof\(List<>\)\.MakeGenericType\(t\.GetGenericArguments\(\)\[0\]\)\)\s*=> ConvertRemoteValuesToGenericList<TResult>\(a\.Value, typeof\(List<>\)\.MakeGenericType\(t\.GetGenericArguments\(\)\[0\]\)\),)'

new_cases = r'''\1
            (MapRemoteValue m, Type t) when t.IsGenericType && t.GetGenericArguments().Length == 2 && t.IsAssignableFrom(typeof(Dictionary<,>).MakeGenericType(t.GetGenericArguments()))
                => ConvertRemoteValuesToDictionary<TResult>(m.Value, typeof(Dictionary<,>).MakeGenericType(t.GetGenericArguments())),
            (ObjectRemoteValue o, Type t) when t.IsGenericType && t.GetGenericArguments().Length == 2 && t.IsAssignableFrom(typeof(Dictionary<,>).MakeGenericType(t.GetGenericArguments()))
                => ConvertRemoteValuesToDictionary<TResult>(o.Value, typeof(Dictionary<,>).MakeGenericType(t.GetGenericArguments())),'''

content = re.sub(list_case_pattern, new_cases, content)

# 2. Add the new method after ConvertRemoteValuesToGenericList method
# Find the end of ConvertRemoteValuesToGenericList method and add the new method
generic_list_method_end = r'(return \(TResult\)list;\s*\n    \})'

new_method = r'''\1

    private static TResult ConvertRemoteValuesToDictionary<TResult>(IReadOnlyList<IReadOnlyList<RemoteValue>>? remoteValues, Type dictionaryType)
    {
        var typeArgs = dictionaryType.GetGenericArguments();
        var dict = (System.Collections.IDictionary)Activator.CreateInstance(dictionaryType)!;

        if (remoteValues is not null)
        {
            var convertKeyMethod = typeof(RemoteValue).GetMethod(nameof(ConvertTo))!.MakeGenericMethod(typeArgs[0]);
            var convertValueMethod = typeof(RemoteValue).GetMethod(nameof(ConvertTo))!.MakeGenericMethod(typeArgs[1]);

            foreach (var pair in remoteValues)
            {
                if (pair.Count != 2)
                {
                    throw new FormatException($"Expected a pair of RemoteValues for dictionary entry, but got {pair.Count} values.");
                }

                var convertedKey = convertKeyMethod.Invoke(pair[0], null)!;
                var convertedValue = convertValueMethod.Invoke(pair[1], null);
                dict.Add(convertedKey, convertedValue);
            }
        }

        return (TResult)dict;
    }'''

content = re.sub(generic_list_method_end, new_method, content)

with open(file_path, 'w') as f:
    f.write(content)

print("Python patch applied successfully")
PYTHON_SCRIPT

echo "Patch applied successfully."
