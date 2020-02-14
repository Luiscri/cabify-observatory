`<spider-chart>` is a web component designed to study categories present 
in Tweets. The axis in radar describes each category. This web component obtains 
data from an elasticSearch index.

### Usage

This web component accept the following parameters:

```html

<spider-chart
    index="<!-- your elasticsearch index -->"
    subindex="<!-- your elasticsearch doc-type -->"
    query="{{query}}"
    fields='["<!-- elasticsearch fields -->"]'>
</spider-chart>

```

### Installation

This web component is available in bower. 

```bash

$ bower install spider-chart

```

This command will install it inside `bower_components` folder


