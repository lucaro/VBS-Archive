## AVS Judgements from VBS
- This directory contains the manual judgements in TRECVID format for AVS tasks that were used for VBS2021 - VBS2024. For each year there are:
  - in msb, a text file with judgements in TRECVID AVS format, using the TRECVID master shot boundaries
  - in ownshots, a text file with judgements in TRECVID AVS format using shots based on the actual judgements, with the *.tsv files describing these shots in TRECVID reference shot format
  - in ownshots, a _dres text file with judgements in a format similar to TRECVID AVS ground truth, but instead of referring to shot IDs it is self-contained, with shot start/end in frames and seconds
- The corresponding Python code to convert AVS judgements from the DRES to the TRECVID format (as used for the files above) is contained in the file [vbs_judgement2trecvid_avs.py](https://github.com/lucaro/VBS-Archive/blob/main/avsjudgements/vbs_judgement2trecvid_avs.py).
