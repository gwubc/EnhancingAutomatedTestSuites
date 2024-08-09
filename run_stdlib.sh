export PYTHONPATH=/home/gary/llm_pbt


# folder_path="result_llama/PBTFactory_stdlib"
# mkdir -p "$folder_path"
# for i in {0..1}; do
#   nohup python3 -u run_stdlib.py -v \
#                     -o "$folder_path/$i" \
#                     --include_test \
#                     -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done


# folder_path="result_v2/PBTFactory_stdlib"
# mkdir -p "$folder_path"
# for i in {4..5}; do
#   nohup python3 -u run_stdlib.py -v \
#                     -o "$folder_path/$i" \
#                     --include_test \
#                     -p pipeline_pbt_v2 > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done

# folder_path="result_part2/PBTFactory_stdlib"
# mkdir -p "$folder_path"
# for i in {6..8}; do
#   nohup python3 -u run_stdlib.py -v \
#                     -o "$folder_path/$i" \
#                     --include_test \
#                     -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done

# folder_path="result_part2/PBTFactory_stdlib_no_test"
# mkdir -p "$folder_path"
# for i in {6..8}; do
#   nohup python3 -u run_stdlib.py -v \
#                     -o "$folder_path/$i" \
#                     -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done


folder_path="result_part2/PBTFactory_stdlib_with_class_structure"
mkdir -p "$folder_path"
for i in {8..8}; do
  nohup python3 -u run_stdlib.py -v \
                    -o "$folder_path/$i" \
                    --include_test \
                    --include_class_structure \
                    -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
  echo "Process $i PID: $!"
done


# folder_path="result/pbt_baseline_stdlib"
# mkdir -p "$folder_path"
# for i in {3..5}; do
#   nohup python3 -u run_stdlib.py -v \
#                     -o "$folder_path/$i" \
#                     --include_test \
#                     -p pipeline_pbt_base > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done


# folder_path="result/unit_baseline_stdlib"
# mkdir -p "$folder_path"
# for i in {5..5}; do
#   nohup python3 -u run_stdlib.py -v \
#                     -o "$folder_path/$i" \
#                     --include_test \
#                     -p pipeline_unit_base > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done
