# canst

canst is a CAN bus Security Toolbox. Basically it allows one to dump, send, sniff and fuzz CAN bus message in an convenient way. It's a very early version currently, some advanced features are working in progress. 

## Installation

**Stable Version**

pip3 install canst(WIP)

**Development Version**

pip3 install git+https://github.com/xia0long/canst.git

## Example

Before using this tool, please initialize the CAN bus device. Here we use vcan0 as an example.


**dumper**

```sh
canst -i vcan0 dumper

canst -i vcan0 dumper --arb_id_filter 7df --data_filter 021001
```

**sender**
```sh
canst -i vcan0 sender -m 7df#021001 -m 7df#022701

canst -i vcan0  sender -m 001#1f1f1f1f -d 1 -m 002#2f2f2f2f -d 2

canst -i vcan0 sender -fp CANDUMP_LOG_FILE_PATH -l
```

**fuzzer**

```sh
canst -i vcan0 fuzzer random

canst -i vcan0 fuzzer mutate -m 1.3#1.2.3..
```

**sniffer**
```sh
canst -i vcan0 sniffer

canst -i vcan0 sniffer --dbc DBC_FILE_PATH
```

## License

MIT
