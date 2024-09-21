# RestDiff Inspector

RestDiff Inspector is a flexible command-line tool for comparing data from two different REST API endpoints. This tool allows users to specify different key paths for each API, making it adaptable to various API structures and response formats.

## Features

- Compare data from two different REST API endpoints
- Support for different data structures in each API
- Flexible key path specification for data extraction
- Customizable request timeout
- Clear and concise output of differences

## Usage

Run the script using the following command structure:

```bash
$ ./restdiff_inspector.py -u1 <url1> -u2 <url2> -k1 <keys1> -k2 <keys2> [-t <timeout>]
```

## Example

Compare alert rules from two different monitoring systems:

```bash
$ ./restdiff_inspector.py \
  -u1 "http://192.168.2.10/promxy/api/v1/rules" \
  -u2 "http://192.168.2.11/vmalert/api/v1/rules" \
  -k1 "data,groups,rules,name" \
  -k2 "data,groups,alerting_rules,name" \
  -t 10
```

This command will:
1. Fetch data from both API endpoints
2. Extract the specified data using the provided key paths
3. Compare the extracted data
4. Display any differences found

## License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit) for details.
