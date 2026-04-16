#!/usr/bin/env python3
"""
Apply the Hugo PR #14535 fix programmatically to avoid patch whitespace issues.
"""

import os
import re

REPO = "/workspace/hugo"

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def apply_hugo_sites_changes():
    """Update hugolib/hugo_sites.go"""
    path = os.path.join(REPO, "hugolib/hugo_sites.go")
    content = read_file(path)

    # Check if already applied
    if "printSiteDataDeprecationInit" in content:
        print("hugo_sites.go already updated")
        return

    # Replace sync.Once fields
    old = """\tprintUnusedTemplatesInit      sync.Once
\tprintPathWarningsInit         sync.Once
\tprintSiteSitesDeprecationInit sync.Once"""
    new = """\tprintUnusedTemplatesInit            sync.Once
\tprintPathWarningsInit               sync.Once
\tprintSiteSitesDeprecationInit       sync.Once
\tprintSiteDataDeprecationInit        sync.Once
\tprintSiteAllPagesDeprecationInit    sync.Once
\tprintSiteBuildDraftsDeprecationInit sync.Once
\tprintSiteLanguagesDeprecationInit   sync.Once"""
    content = content.replace(old, new)

    # Add Data() method to hugoSitesSitesProvider
    old = """func (sp hugoSitesSitesProvider) Sites() page.Sites {
\treturn slices.Collect(sp.h.allSitesInterface(nil))
}

type progressReporter struct {"""
    new = """func (sp hugoSitesSitesProvider) Sites() page.Sites {
\treturn slices.Collect(sp.h.allSitesInterface(nil))
}

func (sp hugoSitesSitesProvider) Data() map[string]any {
\treturn sp.h.Data()
}

type progressReporter struct {"""
    content = content.replace(old, new)

    write_file(path, content)
    print("hugo_sites.go updated")

def apply_site_changes():
    """Update hugolib/site.go"""
    path = os.path.join(REPO, "hugolib/site.go")
    content = read_file(path)

    # Check if already applied
    if "// Deprecated: Use hugo.Data instead." in content:
        print("site.go already updated")
        return

    # Update comment and HugoInfoOptions
    content = content.replace(
        "// Create a sites provider that avoids naming conflict with HugoSites.Sites field.",
        "// Create providers that avoid naming conflicts with HugoSites fields."
    )

    # Update HugoInfoOptions initialization
    old = """\topts := page.HugoInfoOptions{
\t\tConf:          h.Configs.GetFirstLanguageConfig(),
\t\tSitesProvider: sp,
\t\tDeps:          dependencies,
\t}"""
    new = """\topts := page.HugoInfoOptions{
\t\tConf:                      h.Configs.GetFirstLanguageConfig(),
\t\tHugoInfoHugoSitesProvider: sp,
\t\tDeps:                      dependencies,
\t}"""
    content = content.replace(old, new)

    # Update Site.Data() with deprecation
    old = """// Returns a map of all the data inside /data.
func (s *Site) Data() map[string]any {
\treturn s.h.Data()
}"""
    new = """// Returns a map of all the data inside /data.
// Deprecated: Use hugo.Data instead.
func (s *Site) Data() map[string]any {
\ts.h.printSiteDataDeprecationInit.Do(func() {
\t\thugo.Deprecate(".Site.Data", "Use hugo.Data instead.", "v0.156.0")
\t})
\treturn s.h.Data()
}"""
    content = content.replace(old, new)

    # Update Site.BuildDrafts() with deprecation
    old = """func (s *Site) BuildDrafts() bool {
\treturn s.conf.BuildDrafts
}"""
    new = """// Deprecated: See https://discourse.gohugo.io/t/56732.
func (s *Site) BuildDrafts() bool {
\ts.h.printSiteBuildDraftsDeprecationInit.Do(func() {
\t\thugo.Deprecate(".Site.BuildDrafts", "See https://discourse.gohugo.io/t/56732.", "v0.156.0")
\t})
\treturn s.conf.BuildDrafts
}"""
    content = content.replace(old, new)

    # Update Site.AllPages() with deprecation
    old = """// AllPages returns all pages for all sites.
func (s *Site) AllPages() page.Pages {
\ts.CheckReady()
\treturn s.h.Pages()
}"""
    new = """// AllPages returns all pages for all sites.
// Deprecated: See https://discourse.gohugo.io/t/56732.
func (s *Site) AllPages() page.Pages {
\ts.h.printSiteAllPagesDeprecationInit.Do(func() {
\t\thugo.Deprecate(".Site.AllPages", "See https://discourse.gohugo.io/t/56732.", "v0.156.0")
\t})
\ts.CheckReady()
\treturn s.h.Pages()
}"""
    content = content.replace(old, new)

    # Update Site.Languages() with deprecation
    old = """func (s *Site) Languages() langs.Languages {
\treturn s.h.Configs.Languages
}"""
    new = """// Deprecated: See https://discourse.gohugo.io/t/56732.
func (s *Site) Languages() langs.Languages {
\ts.h.printSiteLanguagesDeprecationInit.Do(func() {
\t\thugo.Deprecate(".Site.Languages", "See https://discourse.gohugo.io/t/56732.", "v0.156.0")
\t})
\treturn s.h.Configs.Languages
}"""
    content = content.replace(old, new)

    write_file(path, content)
    print("site.go updated")

def apply_page_changes():
    """Update resources/page/page.go"""
    path = os.path.join(REPO, "resources/page/page.go")
    content = read_file(path)

    if "type nopHugoSitesProvider struct{}" in content:
        print("page.go already updated")
        return

    # Replace nopSitesProvider
    old = """type nopSitesProvider struct{}

func (nopSitesProvider) Sites() Sites {
\treturn nil
}"""
    new = """type nopHugoSitesProvider struct{}

func (nopHugoSitesProvider) Sites() Sites {
\treturn nil
}

func (nopHugoSitesProvider) Data() map[string]any {
\treturn nil
}"""
    content = content.replace(old, new)

    # Add DataProvider interface after SitesProvider
    old = """// SitesProvider provide accessors to get sites.
type SitesProvider interface {
\t// Sites returns all sites for all dimensions.
\tSites() Sites
}

// SiteProvider provides access to the current site."""
    new = """// SitesProvider provide accessors to get sites.
type SitesProvider interface {
\t// Sites returns all sites for all dimensions.
\tSites() Sites
}

// DataProvider provides access to the data directory.
type DataProvider interface {
\tData() map[string]any
}

// SiteProvider provides access to the current site."""
    content = content.replace(old, new)

    write_file(path, content)
    print("page.go updated")

def apply_hugoinfo_changes():
    """Update resources/page/hugoinfo.go"""
    path = os.path.join(REPO, "resources/page/hugoinfo.go")
    content = read_file(path)

    if "HugoInfoHugoSitesProvider" in content:
        print("hugoinfo.go already updated")
        return

    # Update hugoInfoProviders struct
    content = content.replace(
        "type hugoInfoProviders struct {\n\tSitesProvider\n}",
        "type hugoInfoProviders struct {\n\tHugoInfoHugoSitesProvider\n}"
    )

    # Add HugoInfoHugoSitesProvider interface before HugoInfoOptions
    old = """// HugoInfoOptions defines the providers required to initialize HugoInfo.
type HugoInfoOptions struct {"""
    new = """// HugoInfoHugoSitesProvider provides what HugoInfo needs from hugolib.HugoSites.
type HugoInfoHugoSitesProvider interface {
\tSitesProvider
\tDataProvider
}

// HugoInfoOptions defines the providers required to initialize HugoInfo.
type HugoInfoOptions struct {"""
    content = content.replace(old, new)

    # Update HugoInfoOptions fields
    old = """type HugoInfoOptions struct {
\tConf          HugoInfoConfigProvider
\tDeps          []*hugo.Dependency
\tSitesProvider SitesProvider
\tCommitHash    string
\tBuildDate     string
\tGoVersion     string
}"""
    new = """type HugoInfoOptions struct {
\tConf                      HugoInfoConfigProvider
\tHugoInfoHugoSitesProvider HugoInfoHugoSitesProvider

\tDeps       []*hugo.Dependency
\tCommitHash string
\tBuildDate  string
\tGoVersion  string
}"""
    content = content.replace(old, new)

    # Update NewHugoInfo
    content = content.replace(
        "if opts.SitesProvider == nil {\n\t\topts.SitesProvider = nopSitesProvider{}\n\t}",
        "if opts.HugoInfoHugoSitesProvider == nil {\n\t\topts.HugoInfoHugoSitesProvider = nopHugoSitesProvider{}\n\t}"
    )
    content = content.replace(
        "hugoInfoProviders: hugoInfoProviders{SitesProvider: opts.SitesProvider},",
        "hugoInfoProviders: hugoInfoProviders{HugoInfoHugoSitesProvider: opts.HugoInfoHugoSitesProvider},"
    )

    write_file(path, content)
    print("hugoinfo.go updated")

def apply_siteidentities_changes():
    """Update resources/page/siteidentities/identities.go"""
    path = os.path.join(REPO, "resources/page/siteidentities/identities.go")
    content = read_file(path)

    if "hugo.Data" in content:
        print("identities.go already updated")
        return

    content = content.replace(
        "// Identifies site.Data.",
        "// Identifies hugo.Data."
    )
    content = content.replace(
        'Data = identity.StringIdentity("site.Data")',
        'Data = identity.StringIdentity("hugo.Data")'
    )

    write_file(path, content)
    print("identities.go updated")

def add_tests():
    """Add tests to hugolib/site_sites_test.go"""
    path = os.path.join(REPO, "hugolib/site_sites_test.go")
    content = read_file(path)

    if "TestHugoDataDeprecation" in content:
        print("tests already added")
        return

    test_code = '''

func TestHugoDataDeprecation(t *testing.T) {
\tfiles := `
-- hugo.toml --
disableKinds = ['page','rss','section','sitemap','taxonomy','term']
-- data/mydata.toml --
v1 = "myvalue"
-- layouts/home.html --
hugo.Data: {{ hugo.Data.mydata.v1 }}|
site.Data: {{ site.Data.mydata.v1 }}|
\t`
\tb := Test(t, files, TestOptInfo())

\tb.AssertFileContent("public/index.html",
\t\t"hugo.Data: myvalue|",
\t\t"site.Data: myvalue|",
\t)
\tb.AssertLogContains(".Site.Data was deprecated")
}

func TestSiteDeprecations(t *testing.T) {
\tfiles := `
-- hugo.toml --
disableKinds = ['rss','sitemap','taxonomy','term']
buildDrafts = true
[languages]
[languages.en]
weight = 1
[languages.fr]
weight = 2
-- content/p1.md --
---
title: Page 1
---
-- layouts/home.html --
AllPages: {{ len .Site.AllPages }}|
BuildDrafts: {{ .Site.BuildDrafts }}|
Languages: {{ len .Site.Languages }}|
\t`
\tb := Test(t, files, TestOptInfo())

\tb.AssertFileContent("public/index.html",
\t\t"AllPages: 3|",
\t\t"BuildDrafts: true|",
\t\t"Languages: 2|",
\t)
\tb.AssertLogContains(".Site.AllPages was deprecated")
\tb.AssertLogContains(".Site.BuildDrafts was deprecated")
\tb.AssertLogContains(".Site.Languages was deprecated")
}
'''

    content = content.rstrip() + test_code

    write_file(path, content)
    print("tests added")

def main():
    apply_hugo_sites_changes()
    apply_site_changes()
    apply_page_changes()
    apply_hugoinfo_changes()
    apply_siteidentities_changes()
    add_tests()
    print("All changes applied successfully!")

if __name__ == "__main__":
    main()
