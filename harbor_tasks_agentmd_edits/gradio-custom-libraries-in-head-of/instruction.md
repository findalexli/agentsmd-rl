# Add `head` parameter to `gr.HTML` for third-party library support

## Problem

The `gr.HTML` component needs a way to inject custom HTML (typically `<script>` and `<link>` tags) into the document `<head>` section. This is essential for loading third-party JavaScript/CSS libraries (like Chart.js) in custom HTML components. Currently, there's no clean way to load external libraries when creating custom visualizations with `gr.HTML`.

## Expected Behavior

Add a `head` parameter to `gr.HTML` that:
1. Accepts a raw HTML string (typically containing `<script src="...">` or `<link>` tags)
2. The content is injected into the document `<head>` before `js_on_load` executes
3. Scripts are deduplicated by `src` and links by `href` so multiple components requiring the same library don't load it twice
4. The `head` value is included in the component's config for frontend rendering

Example usage:
```python
gr.HTML(
    value=[30, 70, 45, 90, 60],
    html_template='<canvas id="chart"></canvas>',
    js_on_load='''
        const canvas = element.querySelector('#chart');
        new Chart(canvas, {
            type: 'bar',
            data: { labels: props.value.map((_, i) => 'Item ' + (i+1)), datasets: [{ data: props.value }] }
        });
    ''',
    head='<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>',
)
```

## Files to Look At

- `gradio/components/html.py` — The `HTML` component class definition
  - `__init__` method needs to accept and store `head` parameter
  - `get_config` method should include `head` in the returned config dict

## Implementation Notes

- Add `head: str | None = None` parameter to `HTML.__init__`
- Store it as `self.head = head`
- Include it in `get_config()` return value
- Follow existing patterns for parameter documentation
