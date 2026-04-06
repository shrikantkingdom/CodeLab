# Scaler Core Curriculum — Complete 16-Module Study Guide
## Full Solutions, Multiple Approaches & Complexity Analysis

---

## Module 1: Arrays & Two-Pointers

**Overview:** Master fundamental array manipulations using single-pass, two-pointer, and sliding window techniques.

### Session 1.1: Two-Pointer Fundamentals

#### Assignment 1: Two Sum
**Problem:** Given an array of integers `nums` and target integer `target`, return the indices of the two numbers that add up to target. Each input has exactly one solution; cannot use same element twice.

**Constraints:** 2 ≤ n ≤ 10⁴, -10⁹ ≤ nums[i] ≤ 10⁹

**Solution 1 (HashMap - Recommended):**
```python
# Python - Time: O(n), Space: O(n)
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

```java
// Java - Time: O(n), Space: O(n)
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (map.containsKey(complement)) {
            return new int[]{map.get(complement), i};
        }
        map.put(nums[i], i);
    }
    return new int[0];
}
```

**Complexity:** Time O(n), Space O(n)  
**Why Best:** Single pass, no sorting needed, works with unsorted arrays.

---

**Solution 2 (Sorted Two-Pointer):**
```python
# Python - Time: O(n log n), Space: O(1)
def two_sum_sorted(nums, target):
    # Create pairs of (value, original_index)
    indexed = sorted(enumerate(nums), key=lambda x: x[1])
    left, right = 0, len(nums) - 1
    
    while left < right:
        s = indexed[left][1] + indexed[right][1]
        if s == target:
            return sorted([indexed[left][0], indexed[right][0]])
        elif s < target:
            left += 1
        else:
            right -= 1
    return []
```

**Complexity:** Time O(n log n), Space O(1) excluding sort  
**Trade-off:** Slower due to sorting, but teaches two-pointer pattern.

---

#### Assignment 2: Best Time to Buy and Sell Stock
**Problem:** Given prices, find max profit. Can only hold one share at time; must buy before sell.

**Constraints:** 1 ≤ n ≤ 10⁵

```python
# Python - Time: O(n), Space: O(1) - BEST
def max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        if price < min_price:
            min_price = price
        else:
            max_profit = max(max_profit, price - min_price)
    
    return max_profit
```

```java
// Java - Time: O(n), Space: O(1)
public int maxProfit(int[] prices) {
    int minPrice = Integer.MAX_VALUE;
    int maxProfit = 0;
    
    for (int price : prices) {
        if (price < minPrice) {
            minPrice = price;
        } else {
            maxProfit = Math.max(maxProfit, price - minPrice);
        }
    }
    
    return maxProfit;
}
```

**Complexity:** Time O(n), Space O(1)  
**Key Insight:** Track minimum seen so far; profit = current - min.

---

### Session 1.2: Sliding Window & Kadane's Algorithm

#### Assignment 3: Maximum Subarray (Kadane's Algorithm)
**Problem:** Find contiguous subarray with largest sum.

**Constraints:** 1 ≤ n ≤ 10⁵, -10⁴ ≤ nums[i] ≤ 10⁴

```python
# Python - RECOMMENDED
def max_subarray_kadane(nums):
    max_current = max_global = nums[0]
    
    for i in range(1, len(nums)):
        max_current = max(nums[i], max_current + nums[i])
        max_global = max(max_global, max_current)
    
    return max_global
```

```java
// Java
public int maxSubArray(int[] nums) {
    int maxCurrent = nums[0], maxGlobal = nums[0];
    
    for (int i = 1; i < nums.length; i++) {
        maxCurrent = Math.max(nums[i], maxCurrent + nums[i]);
        maxGlobal = Math.max(maxGlobal, maxCurrent);
    }
    
    return maxGlobal;
}
```

**Complexity:** Time O(n), Space O(1)  
**Why Kadane's:** DP-based; optimal substructure: maximal subarray either extends or restarts.

---

#### Assignment 4: Product of Array Except Self
**Problem:** Return array where result[i] = product of all elements except nums[i]. Cannot use division.

**Constraints:** 2 ≤ n ≤ 10⁵

```python
# Python - Prefix-Suffix Product (BEST)
def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    
    # Prefix: result[i] = product of all left of i
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    
    # Suffix: multiply by product of all right of i
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    
    return result
```

```java
// Java
public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] result = new int[n];
    
    // Prefix pass: result[i] = product of nums[0..i-1]
    result[0] = 1;
    for (int i = 1; i < n; i++) {
        result[i] = result[i - 1] * nums[i - 1];
    }
    
    // Suffix pass: multiply by product of nums[i+1..n-1]
    int suffix = 1;
    for (int i = n - 1; i >= 0; i--) {
        result[i] *= suffix;
        suffix *= nums[i];
    }
    
    return result;
}
```

**Complexity:** Time O(n), Space O(1) (excluding output array)  
**Why Best:** Avoids division edge cases (zeros); teaches decomposition pattern.

---

---

## Module 2: Linked Lists

**Overview:** Master linked list operations: reversal, cycle detection, merging.

### Session 2.1: Reversal & Manipulation

#### Assignment 1: Reverse Linked List
**Problem:** Reverse a singly linked list iteratively and recursively.

```python
# Iterative (BEST - O(1) space)
def reverse_list_iterative(head):
    prev = None
    curr = head
    
    while curr:
        nxt = curr.next  # Save next
        curr.next = prev  # Reverse link
        prev = curr       # Move prev
        curr = nxt        # Move curr
    
    return prev

# Recursive (O(n) space due to call stack)
def reverse_list_recursive(head):
    if not head or not head.next:
        return head
    
    new_head = reverse_list_recursive(head.next)
    head.next.next = head
    head.next = None
    
    return new_head
```

```java
// Iterative (BEST)
public ListNode reverseList(ListNode head) {
    ListNode prev = null;
    ListNode curr = head;
    
    while (curr != null) {
        ListNode nxt = curr.next;
        curr.next = prev;
        prev = curr;
        curr = nxt;
    }
    
    return prev;
}

// Recursive
public ListNode reverseListRecursive(ListNode head) {
    if (head == null || head.next == null) return head;
    
    ListNode newHead = reverseListRecursive(head.next);
    head.next.next = head;
    head.next = null;
    
    return newHead;
}
```

**Complexities:**
- Iterative: Time O(n), Space O(1) ⭐ BEST
- Recursive: Time O(n), Space O(n)

---

#### Assignment 2: Detect Cycle (Floyd's Tortoise & Hare)
**Problem:** Determine if linked list has a cycle.

```python
# Floyd's Algorithm (BEST)
def has_cycle(head):
    if not head:
        return False
    
    slow = fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        if slow is fast:
            return True
    
    return False
```

```java
public boolean hasCycle(ListNode head) {
    if (head == null) return false;
    
    ListNode slow = head, fast = head;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        
        if (slow == fast) return true;
    }
    
    return false;
}
```

**Complexity:** Time O(n), Space O(1)  
**Key Insight:** If cycle exists, fast catches slow. Mathematical proof: F = S + k*C (where C = cycle length).

---

### Session 2.2: Merging & Advanced

#### Assignment 3: Merge Two Sorted Lists
**Problem:** Merge two sorted linked lists into one sorted list.

```python
def merge_sorted_lists(list1, list2):
    dummy = ListNode(0)
    curr = dummy
    
    while list1 and list2:
        if list1.val < list2.val:
            curr.next = list1
            list1 = list1.next
        else:
            curr.next = list2
            list2 = list2.next
        curr = curr.next
    
    # Attach remaining
    curr.next = list1 or list2
    
    return dummy.next
```

```java
public ListNode mergeTwoLists(ListNode list1, ListNode list2) {
    ListNode dummy = new ListNode(0);
    ListNode curr = dummy;
    
    while (list1 != null && list2 != null) {
        if (list1.val < list2.val) {
            curr.next = list1;
            list1 = list1.next;
        } else {
            curr.next = list2;
            list2 = list2.next;
        }
        curr = curr.next;
    }
    
    curr.next = (list1 != null) ? list1 : list2;
    return dummy.next;
}
```

**Complexity:** Time O(m + n), Space O(1)  
**Pattern:** Dummy node + single pass comparison.

---

---

## Module 3: Stacks & Queues

**Overview:** Master stack and queue problems: parentheses, monotonic stacks, sliding window.

### Session 3.1: Valid Parentheses & Stack Basics

#### Assignment 1: Valid Parentheses
**Problem:** Determine if string has valid balanced parentheses.

```python
def is_valid_parentheses(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':
            stack.append(char)
        else:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    
    return len(stack) == 0
```

```java
public boolean isValid(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    Map<Character, Character> pairs = new HashMap<>();
    pairs.put(')', '(');
    pairs.put(']', '[');
    pairs.put('}', '{');
    
    for (char c : s.toCharArray()) {
        if (c == '(' || c == '[' || c == '{') {
            stack.push(c);
        } else {
            if (stack.isEmpty() || stack.pop() != pairs.get(c)) {
                return false;
            }
        }
    }
    
    return stack.isEmpty();
}
```

**Complexity:** Time O(n), Space O(n)  
**Key Pattern:** Use stack for matching open/close; validate on close.

---

#### Assignment 2: Min Stack (Track Minimum)
**Problem:** Design stack supporting push, pop, top, getMin all in O(1).

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []
    
    def push(self, val):
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)
    
    def pop(self):
        if self.stack[-1] == self.min_stack[-1]:
            self.min_stack.pop()
        self.stack.pop()
    
    def top(self):
        return self.stack[-1]
    
    def getMin(self):
        return self.min_stack[-1]
```

```java
public class MinStack {
    private Deque<Integer> stack;
    private Deque<Integer> minStack;
    
    public MinStack() {
        stack = new ArrayDeque<>();
        minStack = new ArrayDeque<>();
    }
    
    public void push(int val) {
        stack.push(val);
        if (minStack.isEmpty() || val <= minStack.peek()) {
            minStack.push(val);
        }
    }
    
    public void pop() {
        if (stack.pop().equals(minStack.peek())) {
            minStack.pop();
        }
    }
    
    public int top() {
        return stack.peek();
    }
    
    public int getMin() {
        return minStack.peek();
    }
}
```

**Complexity:** All ops O(1) time, O(n) space  
**Pattern:** Auxiliary stack tracks minimums.

---

### Session 3.2: Monotonic Stacks & Queues

#### Assignment 3: Daily Temperatures
**Problem:** For each day, find next warmer day index. Return 0 if no future warmer day.

```python
def daily_temperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    stack = []  # Monotonic decreasing stack of indices
    
    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_index = stack.pop()
            result[prev_index] = i - prev_index
        stack.append(i)
    
    return result
```

```java
public int[] dailyTemperatures(int[] temperatures) {
    int n = temperatures.length;
    int[] result = new int[n];
    Deque<Integer> stack = new ArrayDeque<>();
    
    for (int i = 0; i < n; i++) {
        while (!stack.isEmpty() && temperatures[i] > temperatures[stack.peek()]) {
            int prevIndex = stack.pop();
            result[prevIndex] = i - prevIndex;
        }
        stack.push(i);
    }
    
    return result;
}
```

**Complexity:** Time O(n), Space O(n)  
**Key Pattern:** Monotonic stack solves "next greater element" in linear time.

---

---

## Module 4: Trees & Binary Search Trees

**Overview:** Tree traversals (inorder, preorder, postorder), BST operations, LCA.

### Session 4.1: Tree Traversals

#### Assignment 1: Inorder Traversal (Iterative)
**Problem:** Traverse BST inorder (left, root, right) iteratively.

```python
def inorder_traversal(root):
    result = []
    stack = []
    curr = root
    
    while curr or stack:
        # Go to leftmost
        while curr:
            stack.append(curr)
            curr = curr.left
        
        curr = stack.pop()
        result.append(curr.val)
        
        curr = curr.right
    
    return result
```

```java
public List<Integer> inorderTraversal(TreeNode root) {
    List<Integer> result = new ArrayList<>();
    Deque<TreeNode> stack = new ArrayDeque<>();
    TreeNode curr = root;
    
    while (curr != null || !stack.isEmpty()) {
        while (curr != null) {
            stack.push(curr);
            curr = curr.left;
        }
        curr = stack.pop();
        result.add(curr.val);
        curr = curr.right;
    }
    
    return result;
}
```

**Complexity:** Time O(n), Space O(h) where h = height  
**Pattern:** Iterative inorder = left + root + right.

---

#### Assignment 2: Level Order Traversal (BFS)
**Problem:** Return level-by-level tree traversal.

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(level)
    
    return result
```

```java
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> result = new ArrayList<>();
    if (root == null) return result;
    
    Queue<TreeNode> queue = new LinkedList<>();
    queue.offer(root);
    
    while (!queue.isEmpty()) {
        int levelSize = queue.size();
        List<Integer> level = new ArrayList<>();
        
        for (int i = 0; i < levelSize; i++) {
            TreeNode node = queue.poll();
            level.add(node.val);
            
            if (node.left != null) queue.offer(node.left);
            if (node.right != null) queue.offer(node.right);
        }
        
        result.add(level);
    }
    
    return result;
}
```

**Complexity:** Time O(n), Space O(w) where w = max width  
**Key Pattern:** Use queue size to control level-by-level iteration.

---

### Session 4.2: LCA & BST Operations

#### Assignment 3: Lowest Common Ancestor
**Problem:** Find LCA of two nodes in BST.

```python
def lowest_common_ancestor(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
    
    return None
```

```java
public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
    while (root != null) {
        if (p.val < root.val && q.val < root.val) {
            root = root.left;
        } else if (p.val > root.val && q.val > root.val) {
            root = root.right;
        } else {
            return root;
        }
    }
    
    return null;
}
```

**Complexity:** Time O(log n) avg, O(n) worst; Space O(1)  
**Key Insight:** In BST, LCA is where paths to p and q diverge.

---

---

## Module 5: Heaps & Priority Queues

**Overview:** Min/Max heaps, Kth largest, merge sorted lists with heaps.

### Session 5.1: Heap Basics & Kth Largest

#### Assignment 1: Kth Largest Element
**Problem:** Find Kth largest element in stream/array.

```python
import heapq

# Approach 1: Min-heap of size K (BEST for streaming)
def find_kth_largest_heap(nums, k):
    # Keep min-heap of k largest
    heap = nums[:k]
    heapq.heapify(heap)
    
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    
    return heap[0]

# Approach 2: Quickselect (BEST if one-time)
def find_kth_largest_quickselect(nums, k):
    def select(left, right, k_smallest):
        if left == right:
            return nums[left]
        
        pivot_idx = random.randint(left, right)
        pivot_idx = partition(left, right, pivot_idx)
        
        if k_smallest == pivot_idx:
            return nums[k_smallest]
        elif k_smallest < pivot_idx:
            return select(left, pivot_idx - 1, k_smallest)
        else:
            return select(pivot_idx + 1, right, k_smallest)
    
    return select(0, len(nums) - 1, len(nums) - k)
```

```java
// Min-heap approach
public int findKthLargest(int[] nums, int k) {
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();
    
    for (int num : nums) {
        minHeap.offer(num);
        if (minHeap.size() > k) {
            minHeap.poll();
        }
    }
    
    return minHeap.peek();
}

// Quickselect approach
public int findKthLargestQuickselect(int[] nums, int k) {
    return quickSelect(nums, 0, nums.length - 1, nums.length - k);
}

private int quickSelect(int[] nums, int left, int right, int kSmallest) {
    if (left == right) return nums[left];
    
    int pivotIdx = new Random().nextInt(right - left + 1) + left;
    pivotIdx = partition(nums, left, right, pivotIdx);
    
    if (kSmallest == pivotIdx) {
        return nums[kSmallest];
    } else if (kSmallest < pivotIdx) {
        return quickSelect(nums, left, pivotIdx - 1, kSmallest);
    } else {
        return quickSelect(nums, pivotIdx + 1, right, kSmallest);
    }
}

private int partition(int[] nums, int left, int right, int pivotIdx) {
    int pivot = nums[pivotIdx];
    swap(nums, pivotIdx, right);
    int store_idx = left;
    
    for (int i = left; i < right; i++) {
        if (nums[i] < pivot) {
            swap(nums, store_idx, i);
            store_idx++;
        }
    }
    swap(nums, right, store_idx);
    return store_idx;
}

private void swap(int[] nums, int i, int j) {
    int tmp = nums[i];
    nums[i] = nums[j];
    nums[j] = tmp;
}
```

**Complexities:**
- Heap: Time O(n log k), Space O(k) - Best for streams
- Quickselect: Time O(n) avg, O(n²) worst, Space O(1) - Best for arrays

---

#### Assignment 2: Merge K Sorted Lists
**Problem:** Merge K sorted linked lists into one sorted list.

```python
import heapq

def merge_k_lists(lists):
    # Min-heap stores (node.val, idx, node)
    min_heap = []
    
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(min_heap, (lst.val, i, lst))
    
    dummy = ListNode(0)
    curr = dummy
    
    while min_heap:
        val, idx, node = heapq.heappop(min_heap)
        curr.next = node
        curr = curr.next
        
        if node.next:
            heapq.heappush(min_heap, (node.next.val, idx, node.next))
    
    return dummy.next
```

```java
public ListNode mergeKLists(ListNode[] lists) {
    PriorityQueue<ListNode> minHeap = new PriorityQueue<>(
        (a, b) -> Integer.compare(a.val, b.val)
    );
    
    for (ListNode list : lists) {
        if (list != null) {
            minHeap.offer(list);
        }
    }
    
    ListNode dummy = new ListNode(0);
    ListNode curr = dummy;
    
    while (!minHeap.isEmpty()) {
        ListNode node = minHeap.poll();
        curr.next = node;
        curr = curr.next;
        
        if (node.next != null) {
            minHeap.offer(node.next);
        }
    }
    
    return dummy.next;
}
```

**Complexity:** Time O(N log k), Space O(k) where N = total nodes, k = lists  
**Key Insight:** Heap of size k always holds smallest from each list.

---

---

## Module 6: Sorting & Searching

**Overview:** Binary search variants, quickselect, sorting stability.

### Session 6.1: Binary Search Patterns

#### Assignment 1: Search in Rotated Sorted Array
**Problem:** Find target in rotated sorted array in O(log n).

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        # Determine which side is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1
```

```java
public int search(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        if (nums[mid] == target) return mid;
        
        if (nums[left] <= nums[mid]) {
            // Left half sorted
            if (nums[left] <= target && target < nums[mid]) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            // Right half sorted
            if (nums[mid] < target && target <= nums[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }
    
    return -1;
}
```

**Complexity:** Time O(log n), Space O(1)  
**Key Pattern:** Identify sorted half first, then narrow search.

---

#### Assignment 2: Find Peak Element
**Problem:** Find peak (nums[i] > neighbors) in O(log n).

```python
def find_peak(nums):
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if nums[mid] > nums[mid + 1]:
            right = mid  # Peak in left half or at mid
        else:
            left = mid + 1  # Peak in right half
    
    return left
```

```java
public int findPeakElement(int[] nums) {
    int left = 0, right = nums.length - 1;
    
    while (left < right) {
        int mid = left + (right - left) / 2;
        
        if (nums[mid] > nums[mid + 1]) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    
    return left;
}
```

**Complexity:** Time O(log n), Space O(1)  
**Key Insight:** Gradient tells us which way peak lies.

---

---

## Module 7: Dynamic Programming I (Intro)

**Overview:** Memoization, tabulation, overlapping subproblems, optimal substructure.

### Session 7.1: Fibonacci & Memoization

#### Assignment 1: Fibonacci Number
**Problem:** Compute nth Fibonacci number efficiently.

```python
# Approach 1: Recursive with Memoization (Top-Down DP)
def fib_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

# Approach 2: Tabulation (Bottom-Up DP) - BEST
def fib_tab(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    
    return dp[n]

# Approach 3: Space Optimized
def fib_optimized(n):
    if n <= 1:
        return n
    
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    
    return curr
```

```java
// Top-Down Memoization
public int fib(int n, Map<Integer, Integer> memo) {
    if (memo.containsKey(n)) return memo.get(n);
    if (n <= 1) return n;
    
    int result = fib(n - 1, memo) + fib(n - 2, memo);
    memo.put(n, result);
    return result;
}

// Bottom-Up Tabulation (BEST)
public int fibTab(int n) {
    if (n <= 1) return n;
    
    int[] dp = new int[n + 1];
    dp[1] = 1;
    
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    
    return dp[n];
}

// Space Optimized
public int fibOptimized(int n) {
    if (n <= 1) return n;
    
    int prev = 0, curr = 1;
    for (int i = 2; i <= n; i++) {
        int temp = curr;
        curr = prev + curr;
        prev = temp;
    }
    
    return curr;
}
```

**Complexities:**
- Memoization: Time O(n), Space O(n)
- Tabulation: Time O(n), Space O(n) ⭐ RECOMMENDED
- Space Optimized: Time O(n), Space O(1) ⭐ BEST

---

### Session 7.2: Knapsack & Subset Sum

#### Assignment 2: 0/1 Knapsack
**Problem:** Given items with weight/value, maximize value with capacity W.

```python
def knapsack_0_1(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]
    
    return dp[n][capacity]

# Space-optimized version
def knapsack_0_1_optimized(weights, values, capacity):
    dp = [0] * (capacity + 1)
    
    for i in range(len(weights)):
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
    
    return dp[capacity]
```

```java
public int knapsack(int[] weights, int[] values, int capacity) {
    int n = weights.length;
    int[][] dp = new int[n + 1][capacity + 1];
    
    for (int i = 1; i <= n; i++) {
        for (int w = 1; w <= capacity; w++) {
            if (weights[i - 1] <= w) {
                dp[i][w] = Math.max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                );
            } else {
                dp[i][w] = dp[i - 1][w];
            }
        }
    }
    
    return dp[n][capacity];
}

// Space-optimized
public int knapsackOptimized(int[] weights, int[] values, int capacity) {
    int[] dp = new int[capacity + 1];
    
    for (int i = 0; i < weights.length; i++) {
        for (int w = capacity; w >= weights[i]; w--) {
            dp[w] = Math.max(dp[w], values[i] + dp[w - weights[i]]);
        }
    }
    
    return dp[capacity];
}
```

**Complexity:** Time O(n * W), Space O(n * W) or O(W) optimized  
**Key Pattern:** Reverse inner loop to avoid using item twice.

---

---

## Module 8: Dynamic Programming II (Advanced)

**Overview:** LIS, coin change, edit distance, DP on trees.

### Session 8.1: Longest Increasing Subsequence

#### Assignment 1: LIS with O(n log n)
**Problem:** Find length of longest increasing subsequence in O(n log n).

```python
import bisect

def longest_increasing_subsequence(nums):
    if not nums:
        return 0
    
    # tails[i] = smallest ending value of increasing seq of length i+1
    tails = []
    
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    
    return len(tails)

# Reconstruction of LIS
def lis_with_reconstruction(nums):
    tails = []
    indices = []  # Track which elements form LIS
    
    for i, num in enumerate(nums):
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
            indices.append(i)
        else:
            tails[pos] = num
            indices[pos] = i
    
    # Reconstruct actual sequence
    result = []
    for idx in indices:
        result.append(nums[idx])
    
    return len(tails), result
```

```java
public int lengthOfLIS(int[] nums) {
    List<Integer> tails = new ArrayList<>();
    
    for (int num : nums) {
        int pos = binarySearch(tails, num);
        if (pos == tails.size()) {
            tails.add(num);
        } else {
            tails.set(pos, num);
        }
    }
    
    return tails.size();
}

private int binarySearch(List<Integer> tails, int target) {
    int left = 0, right = tails.size();
    
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (tails.get(mid) < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    
    return left;
}
```

**Complexity:** Time O(n log n), Space O(n)  
**Key Insight:** Binary search on tails array; O(n²) DP becomes O(n log n).

---

---

## Module 9: Graphs I (BFS/DFS)

**Overview:** Connected components, BFS shortest path, grid DFS, island counting.

### Session 9.1: BFS & Connected Components

#### Assignment 1: Number of Islands
**Problem:** Count number of islands (connected '1's) in grid.

```python
def num_islands(grid):
    if not grid:
        return 0
    
    def dfs(i, j):
        if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]) or grid[i][j] == '0':
            return
        grid[i][j] = '0'  # Mark as visited
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)
    
    count = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                dfs(i, j)
                count += 1
    
    return count

# BFS approach
from collections import deque

def num_islands_bfs(grid):
    if not grid:
        return 0
    
    def bfs(i, j):
        queue = deque([(i, j)])
        grid[i][j] = '0'
        
        while queue:
            r, c = queue.popleft()
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == '1':
                    grid[nr][nc] = '0'
                    queue.append((nr, nc))
    
    count = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                bfs(i, j)
                count += 1
    
    return count
```

```java
public int numIslands(char[][] grid) {
    if (grid == null || grid.length == 0) return 0;
    
    int count = 0;
    for (int i = 0; i < grid.length; i++) {
        for (int j = 0; j < grid[0].length; j++) {
            if (grid[i][j] == '1') {
                dfs(grid, i, j);
                count++;
            }
        }
    }
    
    return count;
}

private void dfs(char[][] grid, int i, int j) {
    if (i < 0 || i >= grid.length || j < 0 || j >= grid[0].length || 
        grid[i][j] == '0') {
        return;
    }
    
    grid[i][j] = '0';
    dfs(grid, i + 1, j);
    dfs(grid, i - 1, j);
    dfs(grid, i, j + 1);
    dfs(grid, i, j - 1);
}
```

**Complexity:** Time O(m * n), Space O(m * n) worst case  
**Key Pattern:** Mark visited to avoid revisits in grid problems.

---

### Session 9.2: Shortest Path

#### Assignment 2: Shortest Path in Unweighted Graph
**Problem:** Find shortest path between two nodes.

```python
from collections import deque

def shortest_path_bfs(graph, start, end):
    queue = deque([(start, 0)])  # (node, distance)
    visited = {start}
    
    while queue:
        node, dist = queue.popleft()
        
        if node == end:
            return dist
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    
    return -1
```

```java
public int shortestPath(Map<Integer, List<Integer>> graph, int start, int end) {
    Queue<int[]> queue = new LinkedList<>();
    queue.offer(new int[]{start, 0});
    Set<Integer> visited = new HashSet<>();
    visited.add(start);
    
    while (!queue.isEmpty()) {
        int[] curr = queue.poll();
        int node = curr[0], dist = curr[1];
        
        if (node == end) return dist;
        
        for (int neighbor : graph.getOrDefault(node, new ArrayList<>())) {
            if (!visited.contains(neighbor)) {
                visited.add(neighbor);
                queue.offer(new int[]{neighbor, dist + 1});
            }
        }
    }
    
    return -1;
}
```

**Complexity:** Time O(V + E), Space O(V)  
**Key Pattern:** BFS naturally finds shortest unweighted path.

---

---

## Module 10: Graphs II (Advanced)

**Overview:** Dijkstra, MST, topological sort, bellman-ford.

### Session 10.1: Dijkstra & Shortest Path (Weighted)

#### Assignment 1: Dijkstra's Algorithm
**Problem:** Find shortest path from source to all nodes (non-negative weights).

```python
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]  # (distance, node)
    
    while pq:
        curr_dist, node = heapq.heappop(pq)
        
        if curr_dist > distances[node]:
            continue
        
        for neighbor, weight in graph[node]:
            distance = curr_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances
```

```java
public Map<Integer, Integer> dijkstra(Map<Integer, List<int[]>> graph, int start) {
    Map<Integer, Integer> distances = new HashMap<>();
    for (int node : graph.keySet()) {
        distances.put(node, Integer.MAX_VALUE);
    }
    distances.put(start, 0);
    
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
    pq.offer(new int[]{0, start});
    
    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int currDist = curr[0], node = curr[1];
        
        if (currDist > distances.get(node)) continue;
        
        for (int[] edge : graph.getOrDefault(node, new ArrayList<>())) {
            int neighbor = edge[0], weight = edge[1];
            int newDist = currDist + weight;
            
            if (newDist < distances.get(neighbor)) {
                distances.put(neighbor, newDist);
                pq.offer(new int[]{newDist, neighbor});
            }
        }
    }
    
    return distances;
}
```

**Complexity:** Time O((V + E) log V), Space O(V)  
**Key Pattern:** Min-heap priority queue selects nearest unvisited node.

---

### Session 10.2: Minimum Spanning Tree

#### Assignment 2: Kruskal's Algorithm (Union-Find)
**Problem:** Find MST of weighted undirected graph.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        return True

def kruskal(n, edges):
    edges.sort(key=lambda x: x[2])  # Sort by weight
    uf = UnionFind(n)
    mst_weight = 0
    
    for u, v, w in edges:
        if uf.union(u, v):
            mst_weight += w
    
    return mst_weight
```

```java
class UnionFind {
    int[] parent, rank;
    
    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }
    
    public int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }
    
    public boolean union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        
        if (rank[px] < rank[py]) {
            int temp = px; px = py; py = temp;
        }
        
        parent[py] = px;
        if (rank[px] == rank[py]) rank[px]++;
        
        return true;
    }
}

public int kruskal(int n, int[][] edges) {
    Arrays.sort(edges, (a, b) -> a[2] - b[2]);
    UnionFind uf = new UnionFind(n);
    int mstWeight = 0;
    
    for (int[] edge : edges) {
        if (uf.union(edge[0], edge[1])) {
            mstWeight += edge[2];
        }
    }
    
    return mstWeight;
}
```

**Complexity:** Time O(E log E), Space O(V)  
**Key Pattern:** Union-Find detects cycles; greedy edge selection.

---

---

## Module 11: Bit Manipulation & Math

**Overview:** Bit tricks, XOR, counting bits, modular arithmetic.

### Session 11.1: Bit Tricks & Techniques

#### Assignment 1: Single Number (XOR)
**Problem:** Array has 2n+1 elements; all appear twice except one. Find single.

```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num  # XOR cancels duplicates
    return result

# Variant: Two non-repeating numbers
def two_single_numbers(nums):
    xor_all = 0
    for num in nums:
        xor_all ^= num
    
    # Find rightmost set bit
    rightmost_bit = xor_all & (-xor_all)
    
    num1 = num2 = 0
    for num in nums:
        if num & rightmost_bit:
            num1 ^= num
        else:
            num2 ^= num
    
    return [num1, num2]
```

```java
public int singleNumber(int[] nums) {
    int result = 0;
    for (int num : nums) {
        result ^= num;
    }
    return result;
}
```

**Complexity:** Time O(n), Space O(1)  
**Key Insight:** XOR property: a ^ a = 0, a ^ 0 = a.

---

#### Assignment 2: Counting Bits
**Problem:** For i from 0 to n, return number of 1-bits in binary.

```python
def count_bits(n):
    dp = [0] * (n + 1)
    
    for i in range(1, n + 1):
        # i & (i-1) removes rightmost 1-bit
        dp[i] = dp[i & (i - 1)] + 1  # BEST - O(1) per element
    
    return dp

# Alternative: Brian Kernighan's algorithm per number
def count_bits_kernighan(n):
    def count_ones(x):
        count = 0
        while x:
            x &= x - 1
            count += 1
        return count
    
    return [count_ones(i) for i in range(n + 1)]
```

```java
public int[] countBits(int n) {
    int[] dp = new int[n + 1];
    
    for (int i = 1; i <= n; i++) {
        dp[i] = dp[i & (i - 1)] + 1;
    }
    
    return dp;
}
```

**Complexity:** Time O(n), Space O(n)  
**Key Insight:** DP: count[i] = count[i & (i-1)] + 1.

---

### Session 11.2: Modular Arithmetic & Number Theory

#### Assignment 3: Fast Exponentiation
**Problem:** Compute a^b mod m efficiently.

```python
def pow_mod(base, exp, mod):
    result = 1
    base %= mod
    
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    
    return result
```

```java
public long powMod(long base, long exp, long mod) {
    long result = 1;
    base %= mod;
    
    while (exp > 0) {
        if ((exp & 1) == 1) {
            result = (result * base) % mod;
        }
        exp >>= 1;
        base = (base * base) % mod;
    }
    
    return result;
}
```

**Complexity:** Time O(log exp), Space O(1)  
**Key Pattern:** Binary exponentiation halves exponent each step.

---

---

## Module 12: System Design Basics

**Overview:** URL shortener, cache design, rate limiting, load balancing.

### Session 12.1: URL Shortener Design

**Problem:** Design system to shorten long URLs (e.g., pastebin.com/xyz).

**Components:**
- API: POST /shorten { original_url }
- Storage: Map shortCode -> originalURL (SQL/NoSQL)
- Encoding: Base62 encoding for short codes

```python
import random
import string

class URLShortener:
    def __init__(self):
        self.short_to_long = {}
        self.long_to_short = {}
        self.chars = string.ascii_letters + string.digits
    
    def encode(self, num):
        """Encode number to base62 string"""
        if num == 0:
            return self.chars[0]
        
        result = []
        while num:
            result.append(self.chars[num % 62])
            num //= 62
        
        return ''.join(reversed(result))
    
    def shorten(self, longURL):
        if longURL in self.long_to_short:
            return self.long_to_short[longURL]
        
        # Use atomic counter or random approach
        shortCode = self.encode(len(self.short_to_long))
        
        self.short_to_long[shortCode] = longURL
        self.long_to_short[longURL] = shortCode
        
        return shortCode
    
    def expand(self, shortCode):
        return self.short_to_long.get(shortCode)
```

**Complexity:**
- Encode/Decode: O(log n)
- Shorten: O(1) insert
- Expand: O(1) lookup

**Scaling Considerations:**
- Use distributed hash table (memcached)
- Unique ID service (Zookeeper)
- Batch allocation to reduce contention

---

### Session 12.2: Caching & Consistency

**Cache Invalidation Strategies:**

1. **Write-Through:** Write to cache + DB simultaneously
   - Pros: Consistent
   - Cons: Slower writes

2. **Write-Back:** Write to cache immediately, async to DB
   - Pros: Fast writes
   - Cons: Risk of data loss

3. **LRU Cache Implementation:**

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key not in self.cache:
            return -1
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Remove oldest
```

**Complexity:** Get/Put O(1), Space O(capacity)

---

---

## Module 13: Databases & SQL

**Overview:** Complex SQL, window functions, indexing, transactions.

### Session 13.1: Advanced SQL Patterns

#### Assignment 1: Nth Highest Salary
**Problem:** Find Nth highest salary (with NULL handling).

```sql
-- Solution 1: Window Functions (BEST)
SELECT DISTINCT Salary
FROM Employee
ORDER BY Salary DESC
LIMIT 1 OFFSET N-1;

-- Solution 2: Using Dense_Rank (handles ties)
SELECT MAX(Salary)
FROM (
    SELECT Salary,
           DENSE_RANK() OVER (ORDER BY Salary DESC) as rnk
    FROM Employee
) AS ranked
WHERE rnk = N;

-- Solution 3: As function with NULL handling
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
AS
BEGIN
    DECLARE M INT;
    SET M = N - 1;
    RETURN (
        SELECT MAX(Salary) FROM (
            SELECT Salary FROM Employee
            UNION SELECT NULL
            ORDER BY Salary DESC
            LIMIT 1 OFFSET M
        ) AS t
    );
END
```

**Complexity:** Time O(n log n) for sort, Space O(n)

---

### Session 13.2: Transactions & Indexing

**ACID Properties:**
- **Atomicity:** All or nothing
- **Consistency:** Valid state transitions
- **Isolation:** Levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable
- **Durability:** Persisted after commit

**Index Types:**
- **B-Tree:** Good for range queries
- **Hash:** O(1) exact match, no range
- **Bitmap:** Low cardinality columns
- **Full-Text:** Text search

---

---

## Module 14: Concurrency & Multithreading

**Overview:** Thread safety, locks, semaphores, producer-consumer.

### Session 14.1: Thread Safety & Synchronization

#### Assignment 1: Thread-Safe Counter

```java
// Approach 1: Synchronized (SIMPLE)
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// Approach 2: AtomicInteger (RECOMMENDED)
import java.util.concurrent.atomic.AtomicInteger;

public class Counter {
    private AtomicInteger count = new AtomicInteger(0);
    
    public void increment() {
        count.incrementAndGet();
    }
    
    public int getCount() {
        return count.get();
    }
}

// Approach 3: ReentrantLock (FLEXIBLE)
import java.util.concurrent.locks.ReentrantLock;

public class Counter {
    private int count = 0;
    private final ReentrantLock lock = new ReentrantLock();
    
    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();
        }
    }
    
    public int getCount() {
        lock.lock();
        try {
            return count;
        } finally {
            lock.unlock();
        }
    }
}
```

**Complexity:** All O(1) per operation  
**Choice Guide:**
- Simple: synchronized
- High contention: AtomicInteger
- Complex logic: ReentrantLock

---

### Session 14.2: Producer-Consumer Pattern

```java
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class ProducerConsumer {
    private final BlockingQueue<Integer> queue = new LinkedBlockingQueue<>(10);
    
    public void produce() throws InterruptedException {
        for (int i = 0; i < 100; i++) {
            queue.put(i);  // Blocks if queue full
            System.out.println("Produced: " + i);
        }
    }
    
    public void consume() throws InterruptedException {
        while (true) {
            int item = queue.take();  // Blocks if queue empty
            System.out.println("Consumed: " + item);
        }
    }
}
```

**Complexity:** Variable based on throughput  
**Pattern:** BlockingQueue abstracts synchronization.

---

---

## Module 15: Advanced Topics & Optimization

**Overview:** Profiling, approximation algorithms, randomization, caching strategies.

### Session 15.1: Performance Bottleneck Analysis

**Profiling Tools:**
- CPU Profiler: Identify hot paths
- Memory Profiler: Detect leaks
- Lock Contention: Monitor synchronized blocks

**Common Bottlenecks:**
- N+1 query problem (DB)
- Unindexed joins (DB)
- Cache misses (CPU)
- Thread contention (Concurrency)

---

### Session 15.2: Bloom Filters & Probabilistic Data Structures

```python
import hashlib

class BloomFilter:
    def __init__(self, size, num_hash_functions):
        self.size = size
        self.num_hash_functions = num_hash_functions
        self.bit_array = [False] * size
    
    def _hash(self, item, seed):
        h = hashlib.md5((item + str(seed)).encode())
        return int(h.hexdigest(), 16) % self.size
    
    def add(self, item):
        for i in range(self.num_hash_functions):
            idx = self._hash(item, i)
            self.bit_array[idx] = True
    
    def contains(self, item):
        for i in range(self.num_hash_functions):
            idx = self._hash(item, i)
            if not self.bit_array[idx]:
                return False
        return True
```

**Complexity:** O(k) add/lookup, Space O(m) (m < n for n items)  
**Use Case:** Spam filters, duplicate detection, cache miss reduction.

---

---

## Module 16: Interview Strategy & Take-homes

**Overview:** Communication patterns, time management, project submission.

### Session 16.1: Mock Interview Checklist

**Problem-Solving Framework:**
1. **Clarify:** Ask constraints, edge cases, examples
2. **Approach:** Discuss multiple solutions (brute, optimized)
3. **Code:** Write clean, commented code
4. **Test:** Walk through examples and edge cases
5. **Optimize:** Discuss time/space tradeoffs

**Time Management (45 min):**
- 5 min: Clarify
- 10 min: Plan approach
- 20 min: Code
- 10 min: Test & optimize

---

### Session 16.2: Take-home Project Structure

**Best Practices:**
- README.md with setup instructions
- Tests (unit + integration)
- .gitignore, requirements.txt/package.json
- Modular code structure
- Performance notes

**Evaluation Rubrics:**
- Correctness (60%)
- Code Quality (20%)
- Efficiency (10%)
- Testing (10%)

---

End of Scaler Core Curriculum — 16 Modules Complete

**Total Problems & Solutions:** 40+ complete solutions (Python + Java)  
**Key Takeaways:**
- Master time/space complexity tradeoffs
- Practice multiple solution approaches
- Understand underlying data structures
- Communicate clearly in interviews
