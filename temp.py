from clearml import Dataset

dataset = Dataset.create(
         dataset_project="Binary_Classification_Test", dataset_name="DataBases"
    )
dataset.add_files(path='DataBases/')
dataset.upload(chunk_size=100)
dataset.finalize()
print("DataBases uploaded.")