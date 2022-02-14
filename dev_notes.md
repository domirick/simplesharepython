# Developer notes
Under construction
## Communication
- Uses TCP
- `Struct('256s Q')` for metadata _(first transfer this)_
	- 256s for the filename
	- Q for the size of file (unsigned long long)
- Bytes for file _(transfer after metadata)_
	- Default packet size is 32768
	- You can modify packet size in the code, it affects transfer speed
	- Progress bar issues with 65535 bytes

## Functions
