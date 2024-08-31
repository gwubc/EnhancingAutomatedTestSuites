export PYTHONPATH=/home/gary/llm_pbt

folder_path="result_working/PBTFactory_evalplus"
mkdir -p "$folder_path"
for i in {2..3}; do
  nohup python3 -u run_evalplus.py -v \
                    -o "$folder_path/$i" \
                    -p pipeline_PBTFactory > "$folder_path/$i.log" 2>&1 &
  echo "Process $i PID: $!"
done


folder_path="result_working/pbt_base_evalplus"
mkdir -p "$folder_path"
for i in {2..3}; do
  nohup python3 -u run_evalplus.py -v \
                    -o "$folder_path/$i" \
                    -p pipeline_pbt_baseline > "$folder_path/$i.log" 2>&1 &
  echo "Process $i PID: $!"
done


folder_path="result_working/unit_test_baseline_evalplus"
mkdir -p "$folder_path"
for i in {2..3}; do
  nohup python3 -u run_evalplus.py -v \
                    -o "$folder_path/$i" \
                    -p pipeline_unit_test_baseline > "$folder_path/$i.log" 2>&1 &
  echo "Process $i PID: $!"
done
