import networkx as nx

from WBBTree import WBBTree
from AdjacencyTree import AdjacencyTree

from BBTree import BBTree
import BBTree as bbt

#don't touch
LEFT = 0
RIGHT = 1


class EulerTourTree(WBBTree):

    def __init__(self, dc, node, level = -1, active = False):

        # we an EulerTree Node initialize it with zero weight
        super().__init__(0)
        # reference to DynamicCon structure this EulerTree node belongs
        self.dc = dc
        # corresponding networkx node, this is a key, access node with G.nodes[node]
        self.node = node
        # level E_i which this node is stored on
        self.level = level
        # active denotes if this node is the active occurence
        self.active = active
        # left and right edge of node in EulerTree, left edge is represented by
        # (predecessor, node), right edge is (node, successor)
        self.edge_occurences = [None, None]

    def __repr__(self):
        output_string = "ETT(node:{}, edge_occurences:{})".format(self.node, self.edge_occurences)
        #output_string = "ETT(dc:{},level:{},node:{})".format(self.dc.max_level, self.level, self.node)
        return output_string

    # acts as a second constructor, creates a new EulerTourTree occurence from
    # an active occurence
    def create_new_occ(self):
        # remember our constructor defaults active to false which is what we want
        new_node = EulerTourTree(self.dc, self.node, self.level)
        return new_node


    def pass_activity(self, to):
        '''pass activity from self to to'''
        if (not self.active):
            raise ValueError("tryna pass activity from an inactive node")
        self.active = false;
        to.active = true;
        to.set_weight(self.weight)
        self.weight = 0
        self.dc.G.nodes[self.node]["data"].active_occ[self.level] = to




################# Static Methods for EulerTourTree ######################

def treeToETList(dc,G,root):
    return treeToETListHelper(dc, G, root, set(),[])

def treeToETListHelper(dc, G,root, processedNodes, ETlist):
    '''processedNodes is a set'''
    ETlist += [EulerTourTree(dc,root,1,False)]
    processedNodes = processedNodes.union(set([root]))
    unprocessedNeighbors = set(list(nx.neighbors(G, root))).intersection(processedNodes)
    if unprocessedNeighbors is not empty:
        for neighbor in list(unprocessedNeighbors):
            ETlist += treeToETListHelper(dc,G,neighbor,processedNodes,ETlist)
    return ETlist



# i is the level, changes root from old_root to new new_root
# make new root first in EulerTour
def change_root(old_root, new_root, i, dc):
    # first node in inorder Traversal
    first_node = old_root.first()
    # if new_root is already the first node we are done
    if new_root is first_node:
        return new_root

    # create new occurence that will arise from changing root
    new_occ = new_root.create_new_occ()

    # we now last node in EulerTour is the old_root
    last_node = old_root.last()

    if first_node.active:
        # make the last occurence of root to be the active
        first_node.pass_activity(last_node)

    ## NOTSURE: what if these edge occurences are None
    if (new_root.edge_occurences[LEFT] == new_root.edge_occurences[RIGHT]):
        k = 0
        # replace none pointer to this new occurence
        edge = new_root.edge_occurences[LEFT]
        while True:
            if dc.G.edges[edge]["data"].tree_occ[i][k] is not None:
                k += 1
            else:
                dc.G.edges[edge]["data"].tree_occ[i][k] = new_occ
                break
    else:
        k = 0
        # replace new_root with this new occurence
        edge = new_root.edge_occurences[LEFT]
        while True:
            if dc.G.edges[edge]["data"].tree_occ[i][k] is not new_root:
                k += 1
            else:
                dc.G.edges[edge]["data"].tree_occ[i][k] = new_occ
                break

    # edge is represented by tuple
    first_edge = first_node.edge_occurences[RIGHT]
    if first_edge != last_node.edge_occurences[LEFT] or new_root is last_node:
        k = 0
        # find pointer to first node
        while True:
            if dc.G.edges[first_edge]["data"].tree_occ[i][k] is not first_node:
                k += 1
            else:
                dc.G.edges[first_edge]["data"].tree_occ[i][k] = last_node
                break
    else:
        k = 0
        # find poitner to first node
        while True:
            if dc.G.edges[first_edge]["data"].tree_occ[i][k] is not first_node:
                k += 1
            else:
                dc.G.edges[first_edge]["data"].tree_occ[i][k] = None
                break

    #right edge of first node becomes right edge of last node
    last_node.edge_occurences[RIGHT] = first_edge

    # left edge of new_root becomes left edge of new_occ
    new_occ.edge_occurences[LEFT] = new_root.edge_occurences[LEFT]
    # new root will have no left edge as it is root
    new_root.edge_occurences[LEFT] = None

    # get rid of first_node
    s1, s2 = bbt.split(first_node, RIGHT, dc.et_dummy)
    # when u see a deletion of a node, isolate
    first_node.isolate()

    s1, s2 = bbt.split(new_root, LEFT, dc.et_dummy)

    s3 = bbt.join(s1, new_occ, dc.et_dummy)

    et = bbt.join(s2, s3, dc.et_dummy)

    return et

# contructs new euler tour from linking of nodes u and v,
# need to make sure that u and v are initially disconnected
# edge is of form (u, v)
def et_link(u, v, edge, i, dc):
    # nodes u,v, i is the level, dc is the pointer to the DynamicCon object

    # get active occurence of the nodes
    u_active = dc.G.nodes[u]["data"].active_occ[i]
    v_active = dc.G.nodes[v]["data"].active_occ[i]

    new_u_occ = u_active.create_new_occ()

    # et tree containing v_active
    et_v = v_active.find_root()

    #reroot et_v at v_active
    et_v = change_root(et_v, v_active, i, dc)

    # initialize first 2 of 4 tree occurences corresponding to this edge
    dc.G.edges[edge]["data"].tree_occ[i][0] = u_active
    dc.G.edges[edge]["data"].tree_occ[i][1] = new_u_occ

    # get last in InOrder traversal of et_v, also since we rerooted (with respect
    # to EulerTour, not the binary tree holding ET(v)) at v_active, we know that
    # v_active = et_v = et_v.first()
    et_v_last = et_v.last()
    dc.G.edges[edge]["data"].tree_occ[i][3] = et_v_last
    # if they are not the same occurence of the same node
    if et_v_last is not v_active:
        dc.G.edges[edge]["data"].tree_occ[i][2] = v_active
    else:
        dc.G.edges[edge]["data"].tree_occ[i][2] = None

    # update tree occurences of our edge following our the edge after u
    after_u_edge = u_active.edge_occurences[RIGHT]
    if after_u_edge:
        if u_active.edge_occurences[LEFT] != after_u_edge:
            k = 0
            # find pointer to u_active
            while True:
                if dc.G.edges[after_u_edge]["data"].tree_occ[i][k] is not u_active:
                    k += 1
                else:
                    dc.G.edges[after_u_edge]["data"].tree_occ[i][k] = new_u_occ
                    break
        else:
            k = 0
            # find pointer to u_active
            while True:
                if dc.G.edges[after_u_edge]["data"].tree_occ[i][k] is not None:
                    k += 1
                else:
                    dc.G.edges[after_u_edge]["data"].tree_occ[i][k] = new_u_occ
                    break

    # update edge_occurences
    new_u_occ.edge_occurences[RIGHT] = u_active.edge_occurences[RIGHT]
    new_u_occ.edge_occurences[LEFT] = edge

    u_active.edge_occurences[RIGHT] = edge
    v_active.edge_occurences[LEFT] = edge

    et_v_last.edge_occurences[RIGHT] = edge


    et_v = bbt.join(et_v, new_u_occ, dc.et_dummy)

    s1, s2 = bbt.split(u_active, RIGHT, dc.et_dummy)

    s3 = bbt.join(et_v, s2, dc.et_dummy)

    et = bbt.join(s1, s3, dc.et_dummy)
    return et





######################################################################





class DynamicConNode():
    def __init__(self):
        # list of EulerTree
        self.active_occ = None
        self.adjacent_edges = None

    def __repr__(self):
        return str(self.active_occ)

class DynamicConEdge:
    def __init__(self):
        self.level = None

        # points to non_tree_edges[level], if this is a tree edge
        # then this is none
        self.non_tree_level_edges = None

        # points to tree_edges[level], if this is a non tree edge
        # then this is none
        self.tree_level_edges = None

        # points to the two ed_nodes corresponding to this edge, are
        # none if this is a tree edge
        self.non_tree_occ = [None, None]

        # points to array for each level the 4 node occurences in EulerTree that
        # represent this edge
        # at each level the four occurences are ordered in the manner below
        # [occurence of source of edge, occurence of source of edge, occurence of target of edge, occurence of target of edge]
        self.tree_occ = None

class DynamicCon:

    def __init__(self, G):
        # G is a networkx graph
        self.G = G

        # number of levels
        logn = 0
        i = len(G.nodes())
        while i > 0:
            logn += 1
            i //= 2

        # constants for asymptotic bounds
        self.small_weight = logn * logn
        self.small_set = 16 * logn
        self.sample_size = 32 * logn * logn
        # this is l in the paper
        self.max_level = 6 * logn
        # counters for number of edges added to each level
        self.added_edges = [0 for _ in range(self.max_level + 1)]
        # rebuild bound of last level, double it as we go up levels
        max_level_bound = 4
        self.rebuild_bound = [max_level_bound * (2**(self.max_level - i)) for _ in range(self.max_level + 1)]

        # edge lists is a list of lists, where each list is the set of edges
        # which we will represent as a tuple on a level
        self.non_tree_edges = [[] for _ in range(self.max_level + 1)]
        self.tree_edges = [[] for _ in range(self.max_level + 1)]
        self.et_dummy = EulerTourTree(self, None)
        g_nodes = self.G.nodes
        for node in g_nodes:
            g_nodes[node]["data"] = DynamicConNode()
            g_nodes[node]["data"].active_occ = [None for _ in range(self.max_level + 1)]
            g_nodes[node]["data"].adjacent_edges = [None for _ in range(self.max_level + 1)]
            for level in range(self.max_level + 1):
                # create euler tree data structure for each node, default it as active_occ
                # as each node is its own EulerTree, thus only one node in the tour
                g_nodes[node]["data"].active_occ[level] = EulerTourTree(self, node, level, True)

        g_edges = self.G.edges
        for edge in g_edges:
            g_edges[edge]["data"] = DynamicConEdge()
            source = edge[0]
            target = edge[1]
            if not self.connected(source, target, 0):
                self.insert_tree(edge, 0, True)
            else:
                self.insert_non_tree(edge, 0)
    # returns boolean of whether the two nodes are in the same tree and thus connected
    def connected(self, u, v, i = None):
        # if no level provided, assume max_level
        if i is None:
            i = self.max_level
        g_nodes = self.G.nodes
        # get active_occ
        u_active_occ = g_nodes[u]["data"].active_occ[i]
        v_active_occ = g_nodes[v]["data"].active_occ[i]

        # if they have the same root
        return(u_active_occ.find_root() is v_active_occ.find_root())

    # Insert edge into F_i, the tree spanning Union G_j , j <= i, where i
    # is the level
    def insert_tree(self, edge, i, create_tree_occ = False):
        # create_tree_occ is to flag signifying if we need to construct list
        # tree_occ for the DynamicCon class

        #endpoints
        u = edge[0]
        v = edge[1]

        # DynamicConEdge
        self.G.edges[edge]["data"].level = i

        # create some empty lists
        if create_tree_occ:
            # 4 node occurences in EulerTree
            self.G.edges[edge]["data"].tree_occ = [[None, None, None, None] for _ in range(self.max_level + 1)]

        ###IMPLEMENT et_link
        for j in range(i, self.max_level + 1):
            et_link(u,v, edge, j, self)
        # edge now has pointer to DynamicCon's tree edges at level i,
        # and add edge to this list
        self.G.edges[edge]["data"].tree_level_edges = self.tree_edges[i].append(edge)

    def insert_non_tree(self, edge, i):
        return

def test1():
    G = nx.Graph()
    for i in range(4):
        G.add_node(i)
    G.add_edge(0,1)
    G.add_edge(0,3)
    G.add_edge(0,2)

    D = DynamicCon(G)
    et_node_0_level_0 = D.G.nodes[0]["data"].active_occ[0]
    print(et_node_0_level_0)
    et_root_0 = et_node_0_level_0.find_root()
    print(et_root_0)
    print("ET(T) on level 0")
    print(et_root_0.in_order())
    #print(p.G.nodes(data = True))



def test2():
    G = nx.Graph()
    for i in range(3):
        G.add_node(i)
    G.add_edge(0,1)
    G.add_edge(1,2)
    p = DynamicCon(G)

    print(str(treeToETList(p, G, i)))


if __name__ == "__main__":
    test1()
