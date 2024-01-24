import os 

all_paths = os.listdir("/Users/devanshu/Desktop/Images/Test/")
root_dir = "/Users/devanshu/Desktop/Images/Test/"

all_paths_a = [root_dir + pat  for pat in all_paths]

labels = [p.split('/')[-1].split('.')[0] for p in all_paths_a] 

def remove_nos(label_list): 
	new_op = [] 	
	for x in label_list:
		new_op.append("".join([y if y.isalpha() else ""   for y in list(x)]))
	
	return new_op 

print(remove_nos(labels))  
	


print("=" * 20 + "paths" ) 
print(all_paths_a) 
print("=" * 20 + "labels") 
print(labels) 
