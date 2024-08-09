export PYTHONPATH=/home/gary/llm_pbt

folder_path="result/PBTFactory_evalplus"
mkdir -p "$folder_path"
for i in {0..5}; do
  nohup python3 -u run_evalplus.py -v \
                    -o "$folder_path/$i" \
                    -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
  echo "Process $i PID: $!"
done
