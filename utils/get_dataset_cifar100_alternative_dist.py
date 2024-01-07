import numpy as np
import torch

from utils.analyse_datasets import analyse_datasets
from utils.load_cifar100 import get_CIFAR100_data



def get_dataset_cifar100_alternative_dist(args):
    """
    In this function, we get the datasets for training and testing.
    """

    # Load the CIFAR100 dataset
    x_train, y_train, x_val, y_val, x_test, y_test = get_CIFAR100_data()

    num_tasks = args.num_tasks
    num_classes = 100

    # Create the tasks
    datasets_tasks = create_tasks_alternative_dist(x_train, y_train, x_val, y_val, x_test, y_test, num_tasks, num_classes, args)

    # Create the dataset for joint training
    # dataset_joint_training = create_joint_training_dataset(x_train, y_train, x_val, y_val, x_test, y_test, num_classes, args)

    return datasets_tasks


def create_tasks_alternative_dist(x_train, y_train, x_val, y_val, x_test, y_test, num_tasks, num_classes, args):

    # Divide the dataset into 2 tasks: 80% of the classes in the first task, 20% in the second task
    # Also, 5% of the classes of the second task are also in the first task
    list_tasks = [80, 100]
    tasks_dict = {}
    for i, value in enumerate(list_tasks):
        previous_value = list_tasks[i-1] if i > 0 else 0
        tasks_dict[i] = list(range(previous_value, value))

    # Add the 5% of the classes of the second task that are also in the first task
    tasks_dict[0].extend(tasks_dict[1][:1])


    datasets_tasks = [] # [train, val, test]

    # Split dataset into tasks based on the tasks_dict
    for key, value in tasks_dict.items():

        train_images = []
        train_labels = []
        val_images = []
        val_labels = []
        test_images = []
        test_labels = []

        # Get the images and labels for the current task
        for i in range(len(y_train)):
            if y_train[i] in value:
                train_images.append(x_train[i])
                train_labels.append(y_train[i])
        for i in range(len(y_val)):
            if y_val[i] in value:
                val_images.append(x_val[i])
                val_labels.append(y_val[i])
        for i in range(len(y_test)):
            if y_test[i] in value:
                test_images.append(x_test[i])
                test_labels.append(y_test[i])

        # Transform the images to tensors. Converting a tensor from a list is extremely slow, so we use numpy arrays
        train_images = torch.tensor(np.array(train_images), dtype=torch.float32)
        train_labels = torch.tensor(np.array(train_labels), dtype=torch.int64)
        val_images = torch.tensor(np.array(val_images), dtype=torch.float32)
        val_labels = torch.tensor(np.array(val_labels), dtype=torch.int64)
        test_images = torch.tensor(np.array(test_images), dtype=torch.float32)
        test_labels = torch.tensor(np.array(test_labels), dtype=torch.int64)

        # Create the datasets
        train_dataset = torch.utils.data.TensorDataset(train_images, train_labels)
        val_dataset = torch.utils.data.TensorDataset(val_images, val_labels)
        test_dataset = torch.utils.data.TensorDataset(test_images, test_labels)

        datasets_tasks.append([train_dataset, val_dataset, test_dataset]) # [train, val, test]
     
    analyse_datasets(datasets_tasks, args)

    return datasets_tasks

