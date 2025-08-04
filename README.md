# Tag Explode

A Python script that processes CSV files to explode tag columns into separate columns.

## Usage

```bash
python tagexplode.py input_file.csv
python tagexplode.py input_file.csv -o output_file.csv
python tagexplode.py input_file.csv -t "tags,categories" -o processed.csv
```

## Arguments

- `input_file`: Path to input CSV file (required)
- `-o, --output`: Output CSV file path (optional, defaults to `input_exploded.csv`)
- `-t, --tag-columns`: Comma-separated tag column names (optional, defaults to `tags`)

## Input Format

Tag columns should contain JSON-like data in one of these formats:

**Dictionary format:**
```
{"environment": "prod", "team": "backend"}
```

**List format:**
```
[{"key": "environment", "value": "prod"}, {"key": "team", "value": "backend"}]
```

## Output

Creates a new CSV with:
- All original columns preserved
- New columns for each discovered tag with `x.` prefix
- Example: `x.environment`, `x.team`

## Example

Input CSV:
```csv
id,name,tags
1,server1,"{""environment"": ""prod"", ""team"": ""backend""}"
2,server2,"{""environment"": ""dev"", ""owner"": ""alice""}"
```

Output CSV:
```csv
id,name,tags,x.environment,x.owner,x.team
1,server1,"{""environment"": ""prod"", ""team"": ""backend""}",prod,,backend
2,server2,"{""environment"": ""dev"", ""owner"": ""alice""}",dev,alice,
```