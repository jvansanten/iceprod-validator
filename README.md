# IceProd validator

A pydantic-based validator that implements a subset of IceProd's config parser,
all in one place and with more helpful error messages.

## Usage

Validate a valid config

	./validate.py examples/21323.json

Introduce some content errors:

	./validate.py <(jq 'del(.tasks[1].name) | .tasks[2].trays[0].data[0].movement="itpit" | del(.tasks[3].trays[0].data[0].remote)' examples/21323.json)
	3 validation errors for Dataset
	tasks -> 1 -> name
	  field required (type=value_error.missing)
	tasks -> 2 -> trays -> 0 -> data -> 0 -> movement
	  value is not a valid enumeration member; permitted: 'input', 'output' (type=type_error.enum; enum_values=[<MovementType.input: 'input'>, <MovementType.output: 'output'>])
	tasks -> 3 -> trays -> 0 -> data -> 0 -> remote
	  remote must be set for input files from permanent storage (type=assertion_error)

Note that this will also catch JSON syntax errors:

	./validate.py <(head examples/21323.json)
	1 validation error for Dataset
	__root__
	  Expecting ',' delimiter: line 11 column 1 (char 247) (type=value_error.jsondecode; msg=Expecting ',' delimiter; doc={
	  "parent_id":20016,
	  "version":3,
	  "options":{},
	  "steering":{
	    "parameters":{
	      "EfficiencyScale":"$steering(EfficiencyScales)[$eval($args(iter) % $len($steering(EfficiencyScales)))]",
	      "EfficiencyScales":[
	        1,
	        3
	; pos=247; lineno=11; colno=1)
