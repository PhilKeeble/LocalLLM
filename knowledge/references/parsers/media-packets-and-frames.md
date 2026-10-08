---
id: reference-parser-media-packets-frames
title: Media containers, codec packets, frame strides and audio sample units
kind: reference
topics: [parsers, media, audio, video, riff, wave, ffmpeg, stride, sample-counts]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Media containers and decoded frames

## RIFF chunk size excludes its header and word padding

Ordinary RIFF chunks have a four-byte identifier and four-byte data length.
Data is padded to a two-byte boundary; length excludes that padding and the
eight-byte header. The outer RIFF size includes its form-type field. [1]

Constructed arithmetic: a child with three data bytes occupies 8+3+1=12 bytes.
After proving the header exists, check the payload and any pad against the
parent's remaining extent using representable arithmetic. Unknown chunks still
need valid skip extents. Do not assume all WAVE files have a fixed 44-byte header
or that a compressed audio block has PCM layout.

## WAVE PCM block alignment and extra-format lengths use bytes

For WAVE_FORMAT_PCM, nBlockAlign equals nChannels*wBitsPerSample/8 and
nAvgBytesPerSec equals nSamplesPerSec*nBlockAlign. Other format tags have their
own rules. WAVEFORMATEX.cbSize counts extra format bytes; PCM ignores it. [2]

Investigative inference: distinguish samples per channel, channels, byte rate,
encoded block and output byte count. Validate the selected format before using
its equation. Checked products still need to match the actual data extent.
Establish serialized header extent independently of native sizeof(WAVEFORMATEX)
before copying or accessing its fields; the API's structure type alone is not
evidence that all those bytes are present in a particular file chunk.

## FFmpeg decoding does not promise one packet per output frame

FFmpeg sends compressed AVPackets with avcodec_send_packet and receives decoded
AVFrames with avcodec_receive_frame. A packet can yield zero, one or multiple
frames. Receive-side EAGAIN requests input; send-side EAGAIN requires receiving
output before retrying. Waiting alone does not advance this state machine. [3]

Investigative inference: separate demultiplexing, codec parsing and output
conversion in the call graph. An accepted packet is not evidence of a produced
frame. Recover ownership and error handling for each stage rather than treating
the container's sample count as the count of immediately available outputs.
Codec configuration and stream selection remain part of the decoding context.

## FFmpeg draining differs from discarding/resetting decoder state

Sending a null packet enters decoder draining mode; receive until AVERROR_EOF
to retrieve buffered output. Resuming afterwards requires avcodec_flush_buffers.
[3]

Investigative inference: EOF at the demultiplexer is not necessarily the final
decoded frame. Track delayed output and the point at which its buffers are
released or published. A seek/reset path that intentionally discards state is
different from finishing a stream. Truncated media and policy cancellation also
need explicit paths; a “flush” label alone does not specify their semantics.

## AVFrame video linesize is signed and can include padding

For video, AVFrame.linesize can be negative, larger than active row data or a
multiple used for field access. AVFrame.data points to the relevant plane data,
not necessarily the lowest address of its storage. [4]

Investigative model: for H>0 rows with base P and signed stride S, visited row
starts are P+y*S for y=0..H-1. Prove the complete accessed span against the owning
plane buffer, including row width; do not simply cast S to an unsigned size.
Compute any magnitude in a domain that can represent it, including the minimum
signed value. Pixel format, plane geometry and crop region need separate evidence.
A negative stride is not by itself memory corruption.

## AVFrame audio nb_samples counts per channel

AVFrame.nb_samples is the number of audio samples per channel. For audio only
linesize[0] is used; planar channels have equally sized planes. Line size can
include padding. Planar audio with more channels than fit in data[] requires
extended_data to access all channels. [4]

Constructed model for interleaved fixed-width samples: N samples per channel,
C channels and B storage bytes per sample require N*C*B payload bytes. A planar
representation instead locates channel planes separately. Recover format and
storage width before applying either model; sample precision need not equal
container width. Do not expose padding as initialized audio merely because it
lies inside the allocation.

## Sources and scope

Reviewed 2026-10-02. RIFF/WAVE rules are scoped examples, not all media containers.
FFmpeg trunk API documentation is not a promise of stable internal struct offsets;
match the target build and API. Formulas are constructed investigation models.
Workflow: `playbook-re-media-font-decoding`.

1. [Microsoft RIFF](https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff-): chunk/header/padding extents.
2. [WAVEFORMATEX](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/ns-mmeapi-waveformatex): format-specific units and cbSize.
3. [FFmpeg send/receive API](https://ffmpeg.org/doxygen/trunk/group__lavc__encdec.html): packet/frame multiplicity, EAGAIN, draining and reset.
4. [FFmpeg AVFrame](https://ffmpeg.org/doxygen/trunk/structAVFrame.html): data, linesize, planes and nb_samples.
