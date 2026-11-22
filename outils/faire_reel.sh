#!/bin/sh
# Usage : sh outils/faire_reel.sh <dossier_serie> <nom> <sortie.mp4>
# Transforme (avec la musique de fond originale outils/musique_fond.m4a) les 5 images 4:5 d'une série en Reel vertical 1080x1920 (30 fps, environ 26 s, transitions glissées).
D=$1; N=$2; O=$3
P="scale=1080:1350,pad=1080:1920:0:285:color=0xe9ebee,fps=30,format=yuv420p"
ffmpeg -y -loglevel error \
 -loop 1 -t 5 -i $D/${N}_1.jpg -loop 1 -t 6 -i $D/${N}_2.jpg -loop 1 -t 6 -i $D/${N}_3.jpg -loop 1 -t 6 -i $D/${N}_4.jpg -loop 1 -t 5 -i $D/${N}_5.jpg \
 -filter_complex "[0]$P[a0];[1]$P[a1];[2]$P[a2];[3]$P[a3];[4]$P[a4];[a0][a1]xfade=transition=slideleft:duration=0.5:offset=4.5[x1];[x1][a2]xfade=transition=slideleft:duration=0.5:offset=10[x2];[x2][a3]xfade=transition=slideleft:duration=0.5:offset=15.5[x3];[x3][a4]xfade=transition=slideleft:duration=0.5:offset=21[v]" \
 -i "$(dirname "$0")/musique_fond.m4a" -map "[v]" -map 5:a -shortest -c:a copy -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -movflags +faststart "$O.tmp.mp4" && mv "$O.tmp.mp4" "$O"
