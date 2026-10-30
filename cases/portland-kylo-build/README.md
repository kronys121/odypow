# Rough cut build (Portland, 2026-09-24)

Scripts that produced `portland_kylo_rough_cut.mp4` (media files are not in git).

Expected layout next to `build/`:
- `build/vo.mp3`, `build/vo.json`: voiceover and its ElevenLabs timestamps
- `video/ref/ppb.mp4`: PPB video "September 24, 2026 Officer-Involved Shooting Body Worn Camera footage"
- `video/src/kylo.jpg`, `video/src/gun.jpg`: photos from the PPB Update #3 page
- `dl/memo.pdf`: Multnomah County DA decline memo

Run:
```bash
python3 gfx.py
python3 edit.py          # add --quick for a fast preview encode
```

Timeline lives in `CH` in `edit.py`: VO chunks with shots keyed to VO time, and `block` entries that
play PPB footage with its original audio. Block C ends at PPB 221.8 s, before the first shot (~221.95 s).
