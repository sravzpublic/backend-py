# Algorithms

### Linked list with arbitrary pointer
```python
import copy
def deep_copy_arbitrary_pointer(head):
  print(dir(head))
  list_orig = copy.deepcopy(head)
  arbitrary_pointer_map = {}
  arbitrary_pointer_reverse = {}
  # Map node -> arbitrary_pointer_data
  arbitrary_pointer_map[list_orig] = list_orig.arbitrary.data
  # Map data -> list node
  arbitrary_pointer_reverse[list_orig.data] = list_orig
  temp_list_pointer = list_orig.next
  head = head.next
  while head:
     temp_list_pointer = copy.deepcopy(head)
     # Map node -> arbitrary_pointer_data
     if temp_list_pointer and temp_list_pointer.arbitrary:
       arbitrary_pointer_map[temp_list_pointer] = temp_list_pointer.arbitrary.data
     # Map data -> list node
     arbitrary_pointer_reverse[temp_list_pointer.data] = temp_list_pointer
     # Move head
     head = head.next
     # Update temp_list_orig node pointer
     temp_list_pointer = temp_list_pointer.next

  for key,item in arbitrary_pointer_map.items():
    key.arbitrary_pointer = arbitrary_pointer_reverse[item]
  return list_orig
```

### Tree level traversal
``` python
# Using two queues
def level_order_traversal(root):
  if root == None:
    return
  result = ""
  queues = [deque(), deque()]

  current_queue = queues[0]
  next_queue = queues[1]

  current_queue.append(root)
  level_number = 0

  while current_queue:
    temp = current_queue.popleft()
    result += str(temp.data) + " "

    if temp.left != None:
      next_queue.append(temp.left)

    if temp.right != None:
      next_queue.append(temp.right)

    if not current_queue:
      level_number += 1
      current_queue = queues[level_number % 2]
      next_queue = queues[(level_number + 1) % 2]
  return result
```

###  Verify Binary Search Tree
```python
def is_bst_rec(root, min_value, max_value):
  if root == None:
    return True

  if root.data < min_value or root.data > max_value:
    return False

  return is_bst_rec(root.left, min_value, root.data) and is_bst_rec(root.right, root.data, max_value)

def is_bst(root):
  return is_bst_rec(root, -sys.maxsize - 1, sys.maxsize)
```

###  Check string segmented
```python
def check_segmented(s, dictionary):
  if len(s) == 0:
    return False
  print("Input string {0}. Range: {1}".format(s, range(len(s))))
  for i in range(len(s)):
    first_word = s[0:i+1]
    second_word = s[i+1:len(s)]
    print("First word {0}. Second word: {1}".format(first_word, second_word))
    if first_word in dictionary:
      if len(second_word) == 0 or second_word in dictionary:
        return True
    else:
      print("First word {0} not in dictionary".format(first_word))
    check_segmented(second_word, dictionary)

def can_segment_string(s, dictionary):
  if check_segmented(s, dictionary):
    return True
  return False

# Check string segmented actual solution
def can_segment_string(s, dictionary):
  for i in range(1, len(s) + 1):
    first = s[0:i]
    if first in dictionary:
      second = s[i:]
      if not second or second in dictionary or can_segment_string(second, dictionary):
        return True
  return False
```

### Reverse words in a sentence
```python
def reverse_words(sentence):    # sentence here is an array of characters
  #TODO: Write - Your -( Code
  sentence_original = sentence
  reversed_list = []
  sentence_list = sentence.tolist()
  len_sentence = len(sentence_list)
  # words = sentence_list.split(' ')
  words = []
  sub_word = []
  for letter in sentence_list:
    if letter != ' ':
      sub_word.append(letter)
    else:
      words.append(''.join(sub_word))
      sub_word = []
  words.append(''.join(sub_word[0:-1]))
  words_reversed = []
  len_words = len(words)
  print("These are words in the sentence {0}".format(words))
  for i in range(len_words):
    print("i: {0} and len_sentence: {1}".format(i, len_words))
    words_reversed.append(words[len_words - 1 - i])
  sentence = list(' '.join(words_reversed))
  sentence.append(sentence_original[-1])
  print("Sentence to be returned: {0}".format(sentence))
  # words = sentence.strip(' ')
  # words = reverse(words)
  # sentence = words.join(' ')
  return sentence

# Reverse string
def str_rev(str, start, end):
  if str == None or len(str) < 2:
    return

  while start < end:
    temp = str[start]
    str[start] = str[end]
    str[end] = temp

    start += 1
    end -= 1
  return str


def reverse_words(sentence):

  # Here sentence is a null-terminated string ending with char '\0'.

  if sentence == None or len(sentence) == 0:
    return

  #  To reverse all words in the string, we will first reverse
  #  the string. Now all the words are in the desired location, but
  #  in reverse order: "Hello World" -> "dlroW olleH".

  str_len = len(sentence)
  sentence = str_rev(sentence, 0, str_len - 2)

  # Now, let's iterate the sentence and reverse each word in place.
  # "dlroW olleH" -> "World Hello"

  start = 0
  end = 0

  while True:

  # find the  start index of a word while skipping spaces.
    while start < len(sentence) and sentence[start] == ' ':
      start += 1

    if start == str_len:
      break

  # find the end index of the word.
    end = start + 1
    while end < str_len and sentence[end] != ' ' and sentence[end] != '\0':
      end += 1

  # let's reverse the word in-place.
    sentence = str_rev(sentence, start, end - 1)
    start = end
  return sentence
```

### Coin denomination
```python
def solve_coin_change(denominations, amount):
  solution = [0] * (amount + 1)
  solution[0] = 1;
  for den in denominations:
    for i in range(den, amount + 1):
      solution[i] += solution[i - den]
      print("solution[i]: {0}. i: {1}. den: {2}".format(solution[i], i, den))
  print(solution[i])

  return solution[len(solution) - 1]
```

### Find kth permuation
```python
def factorial(n):
  if n == 0 or n == 1:
    return 1
  return n * factorial(n -1 )

def find_kth_permutation(v, k, result):
  if not v:
    return

  n = len(v)
  # count is number of permutations starting with first digit
  count = factorial(n - 1)
  selected = (k - 1) // count

  result += str(v[selected])
  del v[selected]
  k = k - (count * selected)
  find_kth_permutation(v, k, result)
```

### Get all sets of numbers
```python
def get_bit(num, bit):
    temp = (1 << bit)
    temp = temp & num
    if temp == 0:
      return 0
    return 1

def get_all_subsets(v, sets):
    subsets_count = 2 ** len(v)
    for i in range(0, subsets_count):
      st = set([])
      for j in range(0, len(v)):
         if get_bit(i, j) == 1:
            st.add(v[j])
      sets.append(st)


def get_all_subsets(v, sets):
  #TODO: Write - Your - Code
  # Append empty set
  sets.append(set([]))
  set_bits = []
  for i in range(1, pow(2, len(v))):
    print("i: {0} - bin: {1}".format(i, list(bin(i))[2:]))
    bits = list(bin(i))[2:]
    while len(bits) < len(v):
      bits = ['0'] + bits
    set_bits.append(bits)
  for bits in set_bits:
    child_set = []
    for index, bit in enumerate(bits):
      if bit == '1':
        child_set.append(v[index])
    sets.append(set(child_set))
  return sets.sort()
```

### Balance braces
```python
import copy

def print_all_braces_rec(n, left_count, right_count, output, result):
  print("Function start: left_count: {0} - right_count: {1} - output: {2}".format(left_count, right_count, output))
  if left_count >= n and right_count >= n:
    result.append(copy.copy(output));
    print("---------------------- Iteration Result: {0}".format(result))

  if left_count < n:
    output += '{'
    print("left_count - output {0}".format(output))
    print_all_braces_rec(n, left_count + 1, right_count, output, result)
    output.pop()

  if right_count < left_count:
    output += '}'
    print("right_count - output {0}".format(output))
    print_all_braces_rec(n, left_count, right_count + 1, output, result)
    output.pop()

def print_all_braces(n):
  output = []
  result = []
  print_all_braces_rec(n, 0, 0, output, result)
  return result
```

### Clone a Directed Graph

```python
import copy
class Node:
  def __init__(self, d):
    self.data = d
    self.neighbors = []

def get_tree_nodes(root, tree_nodes):
  if root in tree_nodes:
    return
  tree_nodes.update({root: root.data})
  for neighbor in root.neighbors:
    get_tree_nodes(neighbor, tree_nodes)

def update_neighbors_of_cloned_node(new_tree, original_tree, cloned_node):
  new_neighbors = []
  node, data = cloned_node
  for neighbor in node.neighbors:
    for new_node in new_tree:
      # neighbor_node, neighbor_data = neighbor
      new_node, new_data = new_node
      if neighbor.data == new_data:
        new_neighbors.append(new_node)
  node.neighbors = new_neighbors

def clone(root):
  # Dicitionary of original tree node -> data
  print("Original root {0}".format(root.data))
  tree_nodes = {}
  cloned_tree_nodes = {}
  cloned_root = None
  # print("Root data: {0} - neighbors: {1}".format(root.data, root.neighbors))
  get_tree_nodes(root, tree_nodes)
  # List of cloned tree node
  tree_nodes_clone = []
  for node in tree_nodes.items():
    tree_nodes_clone.append(copy.copy(node))
  # Update neighors of the cloned tree nodes
  for node in tree_nodes_clone:
    update_neighbors_of_cloned_node(tree_nodes_clone, tree_nodes, node)
    node_object, data = node
    cloned_tree_nodes[node_object] = data
    if data == 0:
      cloned_root = node_object
  print("Original tree nodes: {0}".format(tree_nodes))
  print("Clone tree nodes: {0}".format(cloned_tree_nodes))
  return cloned_root    # return root


  ### Provided solution:
  class Node:
  def __init__(self, d):
    self.data = d
    self.neighbors = []

def clone_rec(root, nodes_completed):
  if root == None:
    return None

  pNew = Node(root.data)
  nodes_completed[root] = pNew

  for p in root.neighbors:
    x = nodes_completed.get(p)
    if x == None:
      pNew.neighbors += [clone_rec(p, nodes_completed)]
    else:
      pNew.neighbors += [x]
  return pNew

def clone(root):
  nodes_completed = {}
  return clone_rec(root, nodes_completed)
```

# Search low and high index
```python
def find_low_index(arr, key, accumulated_index = 0):
 #TODO: Write - Your - Code
  print("Length of array {0} - Mid point {1}", len(arr), len(arr)/2, arr, key, accumulated_index)
  mid_index = int(len(arr)/2)
  if len(arr) == 2:
    if key == arr[0]:
      accumulated_index = accumulated_index + 1
      return accumulated_index
    elif key == arr[1]:
      accumulated_index = accumulated_index + 2
      return accumulated_index
    else:
      return -1
  if key == arr[mid_index]:
    index = 0
    for item in arr:
      index = index + 1
      if item == key:
        break
    accumulated_index = accumulated_index + index - 1
    return accumulated_index
    # return find_low_index(arr[:mid_index], key, accumulated_index = accumulated_index)
  if key < arr[mid_index]:
    return find_low_index(arr[:mid_index], key, accumulated_index = accumulated_index)
  if key > arr[mid_index]:
    accumulated_index = accumulated_index + mid_index
    return find_low_index(arr[mid_index:], key, accumulated_index = accumulated_index)

def find_high_index(arr, key, accumulated_index = 0):
  #TODO: Write - Your - Code
  print("Length of array {0} - Mid point {1}", len(arr), len(arr)/2, arr, key, accumulated_index)
  mid_index = int(len(arr)/2)
  if len(arr) == 2:
    if key == arr[0]:
      accumulated_index = accumulated_index + 1
      return accumulated_index
    elif key == arr[1]:
      accumulated_index = accumulated_index + 2
      return accumulated_index
    else:
      return -1
  if key == arr[mid_index]:
    if len(arr) == 3 and key in arr:
      index = 0
      for item in arr:
        index = index + 1
        if item == key:
          break
      accumulated_index = accumulated_index + index
      return accumulated_index
    accumulated_index = accumulated_index + mid_index
    return find_high_index(arr[mid_index:], key, accumulated_index = accumulated_index)
  if key < arr[mid_index]:
    return find_high_index(arr[:mid_index], key, accumulated_index = accumulated_index)
  if key > arr[mid_index]:
    accumulated_index = accumulated_index + mid_index
    return find_high_index(arr[mid_index:], key, accumulated_index = accumulated_index)

# Actual solution
def find_low_index(arr, key):

  low = 0
  high = len(arr) - 1
  mid = int(high / 2)

  while low <= high:

    mid_elem = arr[mid]

    if mid_elem < key:
      low = mid + 1
    else:
      high = mid - 1

    mid = low + int((high - low) / 2)

  if low < len(arr) and arr[low] == key:
    return low

  return -1

def find_high_index(arr, key):
  low = 0
  high = len(arr) - 1
  mid = int(high / 2)

  while low <= high:
    mid_elem = arr[mid]

    if mid_elem <= key:
      low = mid + 1
    else:
      high = mid - 1

    mid = low + int((high - low) / 2);

  if high == -1:
    return high

  if high < len(arr) and arr[high] == key:
    return high

  return -1
```

# Search rotated array
```python
def binary_search_rotated(arr, key):
  start = 0
  end = len(arr) - 1

  if start > end:
    return -1

  while start <= end:
    mid = start + (end - start) // 2

    if arr[mid] == key:
      return mid

    if arr[start] <= arr[mid] and key <= arr[mid] and key >= arr[start]:
      end = mid - 1

    elif (arr[mid] <= arr[end] and key >= arr[mid] and key <= arr[end]):
      start = mid + 1

    elif arr[start] <= arr[mid] and arr[mid] <= arr[end] and key > arr[end]:
      start = mid + 1

    elif arr[end] <= arr[mid]:
      start = mid + 1

    elif arr[start] >= arr[mid]:
      end = mid - 1

    else:
      return -1

  return -1
```

# Is Binary search tree
```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: Optional[TreeNode], low=-math.inf, high=math.inf) -> bool:
        # Empty tree are valid BST
        if not root:
            return True
        # Current node value must be betten low and high
        if root.val <= low or root.val >= high:
            return False
        return (self.isValidBST(root.left, low, root.val) and self.isValidBST(root.right, root.val, high))

```

# Is symmetric tree
```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:

        def compare_nodes(left, right):
            if (left == None) and (right == None):
                return True
            if (left == None) or (right == None):
                return False
            return (left.val == right.val) and compare_nodes(left.right, right.left) and compare_nodes(left.left, right.right)


        return compare_nodes(root, root)
```

### Zigzag order
```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None
from collections import deque

class Solution:
    def zigzagLevelOrder(self, root):
        """
        :type root: TreeNode
        :rtype: List[List[int]]
        """
        ret = []
        level_list = deque()
        if root is None:
            return []
        # start with the level 0 with a delimiter
        node_queue = deque([root, None])
        is_order_left = True

        while len(node_queue) > 0:
            curr_node = node_queue.popleft()

            if curr_node:
                if is_order_left:
                    level_list.append(curr_node.val)
                else:
                    level_list.appendleft(curr_node.val)

                if curr_node.left:
                    node_queue.append(curr_node.left)
                if curr_node.right:
                    node_queue.append(curr_node.right)
            else:
                # we finish one level
                ret.append(level_list)
                # add a delimiter to mark the level
                if len(node_queue) > 0:
                    node_queue.append(None)

                # prepare for the next level
                level_list = deque()
                is_order_left = not is_order_left

        return ret
```

### Max path sum
```python
class Solution:
    def maxPathSum(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """
        def max_gain(node):
            nonlocal max_sum
            if not node:
                return 0

            # max sum on the left and right sub-trees of node
            left_gain = max(max_gain(node.left), 0)
            right_gain = max(max_gain(node.right), 0)

            # the price to start a new path where `node` is a highest node
            price_newpath = node.val + left_gain + right_gain

            # update max_sum if it's better to start a new path
            max_sum = max(max_sum, price_newpath)

            # for recursion :
            # return the max gain if continue the same path
            return node.val + max(left_gain, right_gain)

        max_sum = float('-inf')
        max_gain(root)
        return max_sum
```

### Word ladd4er
```python
from collections import defaultdict
class Solution(object):
    def ladderLength(self, beginWord, endWord, wordList):
        """
        :type beginWord: str
        :type endWord: str
        :type wordList: List[str]
        :rtype: int
        """

        if endWord not in wordList or not endWord or not beginWord or not wordList:
            return 0

        # Since all words are of same length.
        L = len(beginWord)

        # Dictionary to hold combination of words that can be formed,
        # from any given word. By changing one letter at a time.
        all_combo_dict = defaultdict(list)
        for word in wordList:
            for i in range(L):
                # Key is the generic word
                # Value is a list of words which have the same intermediate generic word.
                all_combo_dict[word[:i] + "*" + word[i+1:]].append(word)


        # Queue for BFS
        queue = collections.deque([(beginWord, 1)])
        # Visited to make sure we don't repeat processing same word.
        visited = {beginWord: True}
        while queue:
            current_word, level = queue.popleft()
            for i in range(L):
                # Intermediate words for current word
                intermediate_word = current_word[:i] + "*" + current_word[i+1:]

                # Next states are all the words which share the same intermediate state.
                for word in all_combo_dict[intermediate_word]:
                    # If at any point if we find what we are looking for
                    # i.e. the end word - we can return with the answer.
                    if word == endWord:
                        return level + 1
                    # Otherwise, add it to the BFS Queue. Also mark it visited
                    if word not in visited:
                        visited[word] = True
                        queue.append((word, level + 1))
                all_combo_dict[intermediate_word] = []
        return 0
```

Is Island
```python
class Solution(object):
    def numIslands(self, grid):
        islands = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == '1':
                    islands += 1
                    self.part_of_island(i,j,grid)
        return islands

    def part_of_island(self, i, j,grid):
        if i < 0 or j < 0 or i == len(grid) or j == len(grid[0]) or grid[i][j] != '1':
            return
        else:
            grid[i][j] = '0'
        self.part_of_island(i,j+1,grid)
        self.part_of_island(i,j-1,grid)
        self.part_of_island(i+1,j,grid)
        self.part_of_island(i-1,j,grid)
```

Course cyclical dependency
```python
class Solution(object):
    def canFinish(self, numCourses, prerequisites):
        """
        :type numCourses: int
        :type prerequisites: List[List[int]]
        :rtype: bool
        """
        from collections import defaultdict
        courseDict = defaultdict(list)

        for relation in prerequisites:
            nextCourse, prevCourse = relation[0], relation[1]
            courseDict[prevCourse].append(nextCourse)

        path = [False] * numCourses
        for currCourse in range(numCourses):
            if self.isCyclic(currCourse, courseDict, path):
                return False
        return True


    def isCyclic(self, currCourse, courseDict, path):
        """
        backtracking method to check that no cycle would be formed starting from currCourse
        """
        if path[currCourse]:
            # come across a previously visited node, i.e. detect the cycle
            return True

        # before backtracking, mark the node in the path
        path[currCourse] = True

        # backtracking
        ret = False
        for child in courseDict[currCourse]:
            ret = self.isCyclic(child, courseDict, path)
            if ret: break

        # after backtracking, remove the node from the path
        path[currCourse] = False
        return ret
```

# Lowest common ancestor
```python
class Solution:

    def __init__(self):
        # Variable to store LCA node.
        self.ans = None

    def lowestCommonAncestor(self, root, p, q):
        """
        :type root: TreeNode
        :type p: TreeNode
        :type q: TreeNode
        :rtype: TreeNode
        """
        def recurse_tree(current_node):

            # If reached the end of a branch, return False.
            if not current_node:
                return False

            # Left Recursion
            left = recurse_tree(current_node.left)

            # Right Recursion
            right = recurse_tree(current_node.right)

            # If the current node is one of p or q
            mid = current_node == p or current_node == q

            # If any two of the three flags left, right or mid become True.
            if mid + left + right >= 2:
                self.ans = current_node

            # Return True if either of the three bool values is True.
            return mid or left or right

        # Traverse the tree
        recurse_tree(root)
        return self.ans
```

# Tree diameter
```python
class Solution:
    def diameterOfBinaryTree(self, root: TreeNode) -> int:
        diameter = 0

        def longest_path(node):
            if not node:
                return 0
            nonlocal diameter
            # recursively find the longest path in
            # both left child and right child
            left_path = longest_path(node.left)
            right_path = longest_path(node.right)

            # update the diameter if left_path plus right_path is larger
            diameter = max(diameter, left_path + right_path)

            # return the longest one between left_path and right_path;
            # remember to add 1 for the path connecting the node and its parent
            return max(left_path, right_path) + 1

        longest_path(root)
        return diameter
```

# Fill color
```python
class Solution(object):
    def floodFill(self, image, sr, sc, newColor):
        R, C = len(image), len(image[0])
        color = image[sr][sc]
        if color == newColor: return image
        def dfs(r, c):
            if image[r][c] == color:
                image[r][c] = newColor
                if r >= 1: dfs(r-1, c)
                if r+1 < R: dfs(r+1, c)
                if c >= 1: dfs(r, c-1)
                if c+1 < C: dfs(r, c+1)

        dfs(sr, sc)
        return image
```

LRU Cache
```python
from collections import OrderedDict
class LRUCache(OrderedDict):

    def __init__(self, capacity):
        """
        :type capacity: int
        """
        self.capacity = capacity

    def get(self, key):
        """
        :type key: int
        :rtype: int
        """
        if key not in self:
            return - 1
        # Item moved to the right end
        self.move_to_end(key)
        return self[key]

    def put(self, key, value):
        """
        :type key: int
        :type value: int
        :rtype: void
        """
        if key in self:
            # Insert at the right end
            self.move_to_end(key)
        self[key] = value
        if len(self) > self.capacity:
            # Pop in FIFO order
            self.popitem(last = False)

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
```

# Min Stack
```python
class MinStack:

    def __init__(self):
        self.stack = []


    def push(self, x: int) -> None:

        # If the stack is empty, then the min value
        # must just be the first value we add
        if not self.stack:
            self.stack.append((x, x))
            return

        current_min = self.stack[-1][1]
        self.stack.append((x, min(x, current_min)))


    def pop(self) -> None:
        self.stack.pop()


    def top(self) -> int:
        return self.stack[-1][0]


    def getMin(self) -> int:
        return self.stack[-1][1]
```

# Serialize tree
# Time O(N) space O(N)
```python
# Serialization
class Codec:

    def serialize(self, root):
        """ Encodes a tree to a single string.
        :type root: TreeNode
        :rtype: str
        """
        def rserialize(root, string):
            """ a recursive helper function for the serialize() function."""
            # check base case
            if root is None:
                string += 'None,'
            else:
                string += str(root.val) + ','
                string = rserialize(root.left, string)
                string = rserialize(root.right, string)
            return string

        return rserialize(root, '')
```

# Deserialize tree
```python
# Deserialization
class Codec:

    def deserialize(self, data):
        """Decodes your encoded data to tree.
        :type data: str
        :rtype: TreeNode
        """
        def rdeserialize(l):
            """ a recursive helper function for deserialization."""
            if l[0] == 'None':
                l.pop(0)
                return None

            root = TreeNode(l[0])
            l.pop(0)
            root.left = rdeserialize(l)
            root.right = rdeserialize(l)
            return root

        data_list = data.split(',')
        root = rdeserialize(data_list)
        return root
```

# Tic Tac Toe
# Time O(n) Space O(n2) 2d array
```python

class TicTacToe {
public:
    vector<vector<int>> board;
    int n;

    TicTacToe(int n) {
        board.assign(n, vector<int>(n, 0));
        this->n = n;
    }

    int move(int row, int col, int player) {
        board[row][col] = player;
        if (checkCol(col, player) ||
            checkRow(row, player) ||
            (row == col && checkDiagonal(player)) ||
            (row == n - col - 1 && checkAntiDiagonal(player))) {
            return player;
        }
        // No one wins
        return 0;
    }

    bool checkDiagonal(int player) {
        for (int row = 0; row < n; row++) {
            if (board[row][row] != player) return false;
        }
        return true;
    }

    bool checkAntiDiagonal(int player) {
        for (int row = 0; row < n; row++) {
            if (board[row][n - row - 1] != player) return false;
        }
        return true;
    }

    bool checkCol(int col, int player) {
        for (int row = 0; row < n; row++) {
            if (board[row][col] != player) return false;
        }
        return true;
    }

    bool checkRow(int row, int player) {
        for (int col = 0; col < n; col++) {
            if (board[row][col] != player) return false;
        }
        return true;
    }
};

```

# Freq stack
```python
class FreqStack(object):

    def __init__(self):
        self.freq = collections.Counter()
        self.group = collections.defaultdict(list)
        self.maxfreq = 0

    def push(self, x):
        f = self.freq[x] + 1 # Default count 0 if element not found
        self.freq[x] = f
        if f > self.maxfreq:
            self.maxfreq = f
        self.group[f].append(x)

    def pop(self):
        # Pop max freq item
        x = self.group[self.maxfreq].pop()
        # Decrement the counter for the item
        self.freq[x] -= 1
        # If no more items for the max freq
        if not self.group[self.maxfreq]:
            # Decrement global max frequence
            self.maxfreq -= 1

        return x
```

# Python reverse integer
```python
        if x >= 2**31-1 or x <= -2**31: return 0
        else:
            strg = str(x)
            if x >= 0 :
                revst = strg[::-1]
            else:
                temp = strg[1:]
                temp2 = temp[::-1]
                revst = "-" + temp2
            if int(revst) >= 2**31-1 or int(revst) <= -2**31: return 0
            else: return int(revst)
```

# Partition label length
```python
class Solution(object):
    def partitionLabels(self, S):
        last = {c: i for i, c in enumerate(S)}
        print(last)
        j = anchor = 0
        ans = []
        for i, c in enumerate(S):
            j = max(j, last[c])
            if i == j:
                ans.append(i - anchor + 1)
                anchor = i + 1

        return ans
```

# Prison cells
```python
class Solution:
    def prisonAfterNDays(self, cells: List[int], N: int) -> List[int]:

        seen = dict()
        is_fast_forwarded = False

        while N > 0:
            # we only need to run the fast-forward once at most
            if not is_fast_forwarded:
                state_key = tuple(cells)
                if state_key in seen:
                    # the length of the cycle is seen[state_key] - N
                    N %= seen[state_key] - N
                    is_fast_forwarded = True
                else:
                    seen[state_key] = N

            # check if there is still some steps remained,
            # with or without the fast-forwarding.
            if N > 0:
                N -= 1
                next_day_cells = self.nextDay(cells)
                cells = next_day_cells

        return cells


    def nextDay(self, cells: List[int]):
        ret = [0]      # head
        for i in range(1, len(cells)-1):
            ret.append(int(cells[i-1] == cells[i+1]))
        ret.append(0)  # tail
        return ret
```

# Sum of two numbers
```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        hashmap = {}
        for i in range(len(nums)):
            complement = target - nums[i]
            if complement in hashmap:
                return [i, hashmap[complement]]
            hashmap[nums[i]] = i
```

# Longest substring
```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        longest_substring_len = 0
        cur_substring = []
        anchor = 0
        for anchor in range(0, len(s)):
            for i in range(anchor, len(s)):
                char = s[i]
                if char in cur_substring:
                    longest_substring_len = max(longest_substring_len, len(cur_substring))
                    cur_substring = []
                    break
                else:
                    cur_substring.append(char)
        return max(longest_substring_len, len(cur_substring))

```

# Tapping rain water
```python
from collections import defaultdict
class Solution:
    def maxArea(self, height: List[int]) -> int:
        maxarea = 0
        l = 0
        r = len(height) - 1

        while (l < r):
            maxarea = max(maxarea, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return maxarea
```
# Interger to roman numeral
```python
class Solution:
    def intToRoman(self, num: int) -> str:
        digits = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
                  (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
                  (5, "V"), (4, "IV"), (1, "I")]

        roman_digits = []
        # Loop through each symbol.
        for value, symbol in digits:
            # We don't want to continue looping if we're done.
            if num == 0: break
            count, num = divmod(num, value)
            # Append "count" copies of "symbol" to roman_digits.
            roman_digits.append(symbol * count)
        return "".join(roman_digits)
```

# Roman to integer
```python
values = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

class Solution:
    def romanToInt(self, s: str) -> int:
        total = 0
        i = 0
        while i < len(s):
            # If this is the subtractive case.
            if i + 1 < len(s) and values[s[i]] < values[s[i + 1]]:
                total += values[s[i + 1]] - values[s[i]]
                i += 2
            # Else this is NOT the subtractive case.
            else:
                total += values[s[i]]
                i += 1
        return total
```
# ThreeSum
```python
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        # Create two sets
        res, dups = set(), set()
        seen = {}
        # Outer enumeration
        for i, val1 in enumerate(nums):
            if val1 not in dups:
                dups.add(val1)
                # enumerate items after current outer enumeration
                for j, val2 in enumerate(nums[i+1:]):
                    complement = -val1 - val2
                    if complement in seen and seen[complement] == i:
                        res.add(tuple(sorted((val1, val2, complement))))
                    seen[val2] = i
        return res
```

# Transpose matrix
```python
class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        n = len(matrix[0])
        for i in range(n // 2 + n % 2):
            for j in range(n // 2):
                tmp = matrix[n - 1 - j][i]
                matrix[n - 1 - j][i] = matrix[n - 1 - i][n - j - 1]
                matrix[n - 1 - i][n - j - 1] = matrix[j][n - 1 -i]
                matrix[j][n - 1 - i] = matrix[i][j]
                matrix[i][j] = tmp
```

# Merge overlapping intervals
```python
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:

        intervals.sort(key=lambda x: x[0])

        merged = []
        for interval in intervals:
            # if the list of merged intervals is empty or if the current
            # interval does not overlap with the previous, simply append it.
            if not merged or merged[-1][1] < interval[0]:
                merged.append(interval)
            else:
            # otherwise, there is overlap, so we merge the current and previous
            # intervals.
                merged[-1][1] = max(merged[-1][1], interval[1])

        return merged
```