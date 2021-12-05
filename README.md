# canst

canst is a CAN bus Security Toolbox. Basically it allows one to dump, send, sinff and fuzz CAN bus message in an convenient way. It's a very early version currently, some advanced features are working in progress. 

## Installation

**Stable Version**

pip3 install canst(WIP)

**Development Version**

pip3 install git+https://github.com/xia0long/canst.git

## Example

**dumper**

```sh
canst dumper

canst dumper --arb_id_filter 7df --data_filter 021001
```

**sender**
```sh
canst sender -m 7df#021001 -m 7df#022701

canst sender -m 001#1f1f1f1f -d 1 -m 002#2f2f2f2f -d 2

canst sender -fp CANDUMP_LOG_FILE_PATH -l
```

**fuzzer**

```sh
canst fuzzer random

canst fuzzer mutate -m 1.3#1.2.3..
```

**sniffer**
```sh
canst sniffer

canst sniffer --dbc DBC_FILE_PATH
```

## License

MIT
