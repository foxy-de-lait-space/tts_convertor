from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import rich.progress
from faster_whisper import WhisperModel
import zipfile
#petit commentaire pour les fouine
model = WhisperModel("tiny", device="cpu")
def format_to_id(id:int,size:int=6):
    return ("0"*(size-len(str(id))))+str(id)
def transcribe(filename):

    segments, info = model.transcribe(filename)
    text_out = ""
    for segment in segments:
        #print(segment.start, segment.end, segment.text)
        text_out  += segment.text

    return text_out



def split_audio(
    input_file,
    output_dir="output",
    min_silence_len=500,      
    silence_thresh=-40,       
    keep_silence=100,         

    base_name = "",
   
):
    os.makedirs(output_dir, exist_ok=True)

    audio = AudioSegment.from_file(input_file)

    parts = detect_nonsilent(audio,
                             min_silence_len=min_silence_len,
                             silence_thresh=silence_thresh)
    
    for part_id,part in enumerate(parts):
        segment = audio[part[0]:part[1]]
        segment : AudioSegment
        segment.export(f"{output_dir}/{base_name}-{part_id}.wav",format="wav")
        #print(segment)

    
    return len(parts)


for file in os.listdir("cut_sounds"):
    os.remove(f"cut_sounds/{file}")
for file in os.listdir("wavs"):
    os.remove(f"wavs/{file}")
file_table = {}
for file in rich.progress.track(os.listdir("sounds"),"cuting..."):
   
   print(f'{file} - {split_audio(f"sounds/{file}",output_dir="cut_sounds",min_silence_len=100,silence_thresh=-39,base_name=file.split(".")[0])} file created.')

file_id = 0

for file in rich.progress.track(os.listdir("cut_sounds"),"transcribing............yes you can make and drink a coffe"):
    out = transcribe(f"cut_sounds/{file}")
    file_table[format_to_id(file_id)+".wav"] = out
    print(f"{file} - text : {out}")
    audio = AudioSegment.from_file(f"cut_sounds/{file}")
    audio.export(f"wavs/{format_to_id(file_id)}.wav",format="wav")
    file_id += 1


metadata = []

for file in file_table:
    metadata.append(f"{file}|{file_table[file]}")
metadata = "\n".join(metadata)
print(metadata)

file = open("tmp_metadata.csv","w")
file.write(metadata)
file.close()

zip = zipfile.ZipFile("out.zip","w")
zip.write("tmp_metadata.csv","metadata.csv")
zip.mkdir("wavs")
for file in os.listdir("wavs"):
    zip.write("wavs/"+file,"wavs/"+file)
zip.close()

print("cleaning...")
print(" - cleaning cut_sounds/ ...")

for file in os.listdir("cut_sounds"):
    os.remove(f"cut_sounds/{file}")


print(" - cleaning wavs/ ...")
for file in os.listdir("wavs"):
    os.remove(f"wavs/{file}")


print(" - deleting tmp.metadata.csv")
os.remove("tmp_metadata.csv")

