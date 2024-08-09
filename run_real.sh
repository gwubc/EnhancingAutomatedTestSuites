export PYTHONPATH=/home/gary/llm_pbt

# folder_path="result/PBTFactory_real_flutils"
# mkdir -p "$folder_path"
# for i in {1..2}; do
#   nohup python3 -u run_real_project.py -v \
#                     -o "$folder_path/$i" \
#                     -d real_project_dataset/flutils/test_data \
#                     --project_src_code real_project_dataset/flutils/flutils \
#                     -p pipeline_pbt_v1 > "$folder_path/$i.log2" 2>&1 &
#   echo "Process $i PID: $!"
# done

# folder_path="result/PBTFactory_real_requests"
# mkdir -p "$folder_path"
# for i in {1..2}; do
#   nohup python3 -u run_real_project.py -v \
#                     -o "$folder_path/$i" \
#                     -d real_project_dataset/requests/test_data \
#                     --project_src_code real_project_dataset/requests/requests \
#                     -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done

# folder_path="result/PBTFactory_real_flask"
# mkdir -p "$folder_path"
# for i in {1..2}; do
#   nohup python3 -u run_real_project.py -v \
#                     -o "$folder_path/$i" \
#                     -d real_project_dataset/flask/test_data \
#                     --project_src_code real_project_dataset/flask/flask \
#                     -p pipeline_pbt_v1 > "$folder_path/$i.log" 2>&1 &
#   echo "Process $i PID: $!"
# done
