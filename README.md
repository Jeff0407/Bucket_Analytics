## Bucket Analytics Auto Broadcasting Branch

### Main idea
  - Using yolo model to distinguish the postion of each players on the court and save the postion to a txt file and then Use the attached file to find the position that contains most players and then zoom in based on the postion we found.
  
### Architecture diagram
  - Step 1: Read the txt file that records the position of each plaer in each frame(read_txt function)
  - Step 2: Project all the postion onto the x-axis and find the max_x_postion using sliding window(find_max_x function)
  - Step 3: Zoom in the frame using max_x_postion as core(zoom function)

  

