import openai


# 设置API密钥
client = openai.OpenAI(api_key="key")
MODEL = "gpt-4o-mini-2024-07-18"

# 上传训练文件并获取文件对象
train_file_obj = client.files.create(
  file=open("input_file_path", "rb"),
  purpose="fine-tune"
)

# 上传验证文件并获取文件对象
valid_file_obj = client.files.create(
  file=open("valid_file_path", "rb"),
  purpose="fine-tune"
)

# 获取上传后的文件ID
training_file_id = train_file_obj.id
validation_file_id = valid_file_obj.id
print(f"Uploaded training file ID: {training_file_id}")
print(f"Uploaded validation file ID: {validation_file_id}")

# 创建微调作业，设置学习率和验证集
fine_tune_job = client.fine_tuning.jobs.create(
  training_file=training_file_id,
  validation_file=validation_file_id, 
  model=MODEL,
  hyperparameters={
    "learning_rate_multiplier": 0.15,
    "batch_size": 16,
    "n_epochs": 2, 
  }
)

# 打印微调作业ID
fine_tune_job_id = fine_tune_job.id
print(f"Fine-tune Job ID: {fine_tune_job_id}")
