#!/bin/bash
set -e

cd /workspace/hugo

# Check if already patched (idempotency check)
if grep -q "func (s \*TemplateStore) parseTemplate(ti \*TemplInfo) error {" tpl/tplimpl/templates.go 2>/dev/null; then
    echo "Already patched"
    exit 0
fi

echo "Applying fix..."

# Fix 1: templates.go - parseTemplate signature
sed -i 's/func (s \*TemplateStore) parseTemplate(ti \*TemplInfo, replace bool) error/func (s *TemplateStore) parseTemplate(ti *TemplInfo) error/g' tpl/tplimpl/templates.go

# Fix 2: templates.go - doParseTemplate call in parseTemplate
sed -i 's/err := s\.tns\.doParseTemplate(ti, replace)/err := s.tns.doParseTemplate(ti)/g' tpl/tplimpl/templates.go

# Fix 3: templates.go - doParseTemplate signature
sed -i 's/func (t \*templateNamespace) doParseTemplate(ti \*TemplInfo, replace bool) error/func (t *templateNamespace) doParseTemplate(ti *TemplInfo) error/g' tpl/tplimpl/templates.go

# Fix 4: templates.go - remove !replace && from two locations
sed -i 's/if !replace && prototype\.Lookup(name) != nil/if prototype.Lookup(name) != nil/g' tpl/tplimpl/templates.go

# Fix 5: templatestore.go - parseTemplates signature
sed -i 's/func (s \*TemplateStore) parseTemplates(replace bool) error/func (s *TemplateStore) parseTemplates() error/g' tpl/tplimpl/templatestore.go

# Fix 6: templatestore.go - change parseTemplates(false) to parseTemplates()
sed -i 's/s\.parseTemplates(false)/s.parseTemplates()/g' tpl/tplimpl/templatestore.go

# Fix 7: templatestore.go - change parseTemplates(true) to parseTemplates()
sed -i 's/s\.parseTemplates(true)/s.parseTemplates()/g' tpl/tplimpl/templatestore.go

# Fix 8: templatestore.go - change s.parseTemplate(vv, replace) to s.parseTemplate(vv)
sed -i 's/s\.parseTemplate(vv, replace)/s.parseTemplate(vv)/g' tpl/tplimpl/templatestore.go

# Fix 9: templatestore.go - change s.parseTemplate(vvv, replace) to s.parseTemplate(vvv)
sed -i 's/s\.parseTemplate(vvv, replace)/s.parseTemplate(vvv)/g' tpl/tplimpl/templatestore.go

echo "Code changes applied"

# Rebuild Hugo binary with the fix
CGO_ENABLED=0 go build -o /usr/local/bin/hugo .

echo "Hugo binary rebuilt with fix"
