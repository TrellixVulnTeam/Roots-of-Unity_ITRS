import random

from godot import exposed, export
from godot.bindings import _File as File
from godot import ArrayMesh
from godot import *
import random as r
import numpy as np
import numpy.lib.mixins
import numbers, time, math
from scipy.special import comb
from itertools import chain
from debugging import debugging
import traceback
import ctypes

COLOR = ResourceLoader.load("res://new_spatialmaterial.tres")


@exposed(tool=False)
class Chunk_Network(MeshInstance):
	phi = 1.61803398874989484820458683
	phi_powers = np.power(np.array([phi] * 100), np.arange(100))
	worldplane = np.array([[phi, 0, 1, phi, 0, -1], [1, phi, 0, -1, phi, 0], [0, 1, phi, 0, -1, phi]])
	normalworld = worldplane / np.linalg.norm(worldplane[0])
	squareworld = normalworld.transpose().dot(normalworld)
	parallelspace = np.array([[-1 / phi, 0, 1, -1 / phi, 0, -1],
							  [1, -1 / phi, 0, -1, -1 / phi, 0],
							  [0, 1, -1 / phi, 0, -1, -1 / phi]])
	normallel = parallelspace / np.linalg.norm(parallelspace[0])
	squarallel = normallel.T.dot(normallel)
	deflation_face_axes = [[2, 1, 1, 1, 1, -1],
						   [1, 2, 1, -1, 1, 1],
						   [1, 1, 2, 1, -1, 1],
						   [1, -1, 1, 2, -1, -1],
						   [1, 1, -1, -1, 2, -1],
						   [-1, 1, 1, -1, -1, 2]]
	ch3 = [[1, 1, 1, 0, 0, 0], [1, 1, 0, 1, 0, 0], [1, 1, 0, 0, 1, 0], [1, 1, 0, 0, 0, 1], [1, 0, 1, 1, 0, 0],
		   [1, 0, 1, 0, 1, 0],
		   [1, 0, 1, 0, 0, 1], [1, 0, 0, 1, 1, 0], [1, 0, 0, 1, 0, 1], [1, 0, 0, 0, 1, 1], [0, 1, 1, 1, 0, 0],
		   [0, 1, 1, 0, 1, 0],
		   [0, 1, 1, 0, 0, 1], [0, 1, 0, 1, 1, 0], [0, 1, 0, 1, 0, 1], [0, 1, 0, 0, 1, 1], [0, 0, 1, 1, 1, 0],
		   [0, 0, 1, 1, 0, 1],
		   [0, 0, 1, 0, 1, 1], [0, 0, 0, 1, 1, 1]]
	twoface_axes = np.array(
		[[1, 1, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0], [1, 0, 0, 1, 0, 0], [1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 0, 1],
		 [0, 1, 1, 0, 0, 0], [0, 1, 0, 1, 0, 0], [0, 1, 0, 0, 1, 0], [0, 1, 0, 0, 0, 1], [0, 0, 1, 1, 0, 0],
		 [0, 0, 1, 0, 1, 0], [0, 0, 1, 0, 0, 1], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 1, 1]])

	twoface_projected = np.array([
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 0]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 1]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 2]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 3]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 4]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 5]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 6]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 7]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 8]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 9]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 10]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 11]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 12]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 13]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 14]]
	])
	twoface_normals = np.cross(twoface_projected[:, 0], twoface_projected[:, 1])
	twoface_normals = twoface_normals / np.linalg.norm(twoface_normals, axis=1)[0]

	twoface_projected_w = np.array([
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 0]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 1]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 2]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 3]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 4]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 5]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 6]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 7]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 8]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 9]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 10]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 11]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 12]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 13]],
		normallel.T[np.nonzero(twoface_axes)[1][np.nonzero(twoface_axes)[0] == 14]]
	])
	twoface_normals_w = np.cross(twoface_projected_w[:, 0], twoface_projected_w[:, 1])
	twoface_normals_w = twoface_normals_w / np.linalg.norm(twoface_normals_w, axis=1)[0]

	possible_centers_live = np.array(
		[[0.5, 0.5, 0.5, 0., 0., 0.], [0.5, 0.5, 2., 1., -1.5, 1.], [0.5, 1., 1.5, 0., -0.5, 1.],
		 [0.5, 1.5, 1., -0.5, 0., 1.], [0.5, 2., 0.5, -1.5, 1., 1.], [0.5, 2., 2., -0.5, -0.5, 2.],
		 [1., 0.5, 1.5, 1., -0.5, 0.], [1., 1.5, 2., 0.5, -0.5, 1.], [1., 1.5, 0.5, -0.5, 1., 0.],
		 [1., 2., 1.5, -0.5, 0.5, 1.], [1.5, 0.5, 1., 1., 0., -0.5], [1.5, 1., 0.5, 0., 1., -0.5],
		 [1.5, 1., 2., 1., -0.5, 0.5], [1.5, 2., 1., -0.5, 1., 0.5], [2., 0.5, 0.5, 1., 1., -1.5],
		 [2., 0.5, 2., 2., -0.5, -0.5], [2., 1., 1.5, 1., 0.5, -0.5], [2., 1.5, 1., 0.5, 1., -0.5],
		 [2., 2., 0.5, -0.5, 2., -0.5], [2., 2., 2., 0.5, 0.5, 0.5]])
	possible_centers = ['[0.5 0.5 0.5 0.  0.  0. ]', '[ 0.5  0.5  2.   1.  -1.5  1. ]',
						'[ 0.5  1.   1.5  0.  -0.5  1. ]',
						'[ 0.5  1.5  1.  -0.5  0.   1. ]', '[ 0.5  2.   0.5 -1.5  1.   1. ]',
						'[ 0.5  2.   2.  -0.5 -0.5  2. ]',
						'[ 1.   0.5  1.5  1.  -0.5  0. ]', '[ 1.   1.5  2.   0.5 -0.5  1. ]',
						'[ 1.   1.5  0.5 -0.5  1.   0. ]',
						'[ 1.   2.   1.5 -0.5  0.5  1. ]', '[ 1.5  0.5  1.   1.   0.  -0.5]',
						'[ 1.5  1.   0.5  0.   1.  -0.5]',
						'[ 1.5  1.   2.   1.  -0.5  0.5]', '[ 1.5  2.   1.  -0.5  1.   0.5]',
						'[ 2.   0.5  0.5  1.   1.  -1.5]',
						'[ 2.   0.5  2.   2.  -0.5 -0.5]', '[ 2.   1.   1.5  1.   0.5 -0.5]',
						'[ 2.   1.5  1.   0.5  1.  -0.5]',
						'[ 2.   2.   0.5 -0.5  2.  -0.5]', '[2.  2.  2.  0.5 0.5 0.5]']

	rhomb_indices = np.array(
		[0, 2, 7, 0, 7, 3, 0, 3, 5, 0, 5, 4, 0, 4, 6, 0, 6, 2, 1, 4, 5, 1, 6, 4, 1, 2, 6, 1, 7, 2, 1, 3, 7, 1, 5, 3])

	player_pos = np.zeros((3,))
	player_guess = None
	block_highlight = ImmediateGeometry.new()
	block_highlight.set_material_override(COLOR)

	def phipow(self, n):
		if n >= 0:
			return self.phi_powers[n]
		if n < 0:
			return 1.0 / self.phi_powers[-n]

	def custom_pow(self, matrix, power, safe_amount=7):
		"""
		A safe method for taking positive and negative powers of integer matrices without getting floating point errors.
		When the power is negative, a positive power is taken first before inverting (the opposite of numpy). When the
		power's absolute value is outside the safe_amount,
		:param matrix: The (square) matrix to be exponentiated. Will be converted to numpy array, dtype=int.
		:param power: The exponent, which should be integer.
		:param safe_amount: Amount to exponentiate at once. Default was obtained via testing; 8 seems fine but went with
		 a default of 7. Higher values, perhaps 10 to 12, are fine if exponents will be positive. Higher values will
		 make performance better if very large exponents are being used.
		:return: A numpy matrix, the power of the input matrix.
		"""
		exponent_increment = safe_amount
		remaining_levels = power
		product = np.eye(len(matrix), dtype='int64')
		trustworthy_portion = np.array(
			np.round(np.linalg.inv(np.linalg.matrix_power(np.array(matrix, dtype='int64'), exponent_increment))), dtype='int64')
		while remaining_levels < -exponent_increment:
			product = np.array(np.round(product.dot(trustworthy_portion)), dtype='int64')
			remaining_levels += exponent_increment
		trustworthy_portion = np.array(
			np.round(np.linalg.matrix_power(np.array(matrix, dtype='int64'), exponent_increment)), dtype='int64')
		while remaining_levels > exponent_increment:
			product = np.array(np.round(product.dot(trustworthy_portion)), dtype='int64')
			remaining_levels -= exponent_increment
		remaining_part = np.linalg.matrix_power(np.array(matrix, dtype='int64'), abs(remaining_levels))
		if remaining_levels < 0:
			remaining_part = np.array(np.round(np.linalg.inv(remaining_part)), dtype='int64')
		return np.array(np.round(product.dot(remaining_part)), dtype='int64')

	def chunk_center_lookup(self, template_index):
		"""
		Returns the chunk's template's center (as an array of six coordinates) given its index.
		This function is needed because all_chosen_centers stores the centers as strings.
		:param template_index: The index of the chunk template within all_chosen_centers, all_blocks, etc.
		:return: The center of the chunk, as block-level coordinates within the template.
		"""
		# TODO Replace with a pre-calculated lookup table ("all_chosen_centers_live")?
		return self.possible_centers_live[self.possible_centers.index(self.all_chosen_centers[template_index])]

	def convert_chunklayouts(self, filename="res://chunklayouts_perf_14"):
		"""
		Loads a pure-Python repr of the chunk layouts (as generated by
		numpylattice.py), and then saves that as three separate files, one
		of which is in the more compact numpy save format.
		"""
		# TODO Identify all the blocks which are always present,
		# 	then exclude those when saving, so they don't have to be loaded.
		# 	Save them in a separate (and of course human-readable) file, or maybe
		# 	as a first element in the layouts file.
		# TODO Figure out all the rotation matrices mapping between chunk
		# 	orientations, so that I can save 1/10th as many of these templates.
		# 	Also, check if other symmetries apply - individual chunks are
		# 	rotationally symmetrical too.
		fs = File()
		constraints_sorted = dict()
		for center in self.possible_centers:
			constraints_sorted[center] = []
		all_constraints = []
		all_blocks = []
		all_chunks = []
		all_counters = []
		all_chosen_centers = []
		all_block_axes = []
		all_sorted_constraints = []
		dupecounter = 0
		transformations = [(np.eye(6), np.eye(15))]  # ,
		#	(np.array(self.chunk_rot1),np.array(self.const_rot1)),
		#	(np.array(self.chunk_rot2),np.array(self.const_rot1).T)]

		for layout_file in [filename]:
			try:
				fs.open(layout_file, fs.READ)
				num_to_load = 100
				while not fs.eof_reached():  # len(all_chunks) < num_to_load:#not fs.eof_reached():
					# relevant chunk as chosen_center string
					ch_c = str(fs.get_line())
					# Constraint is 30 floats
					cstts = np.zeros((30))
					for i in range(30):
						cstts[i] = fs.get_real()
					cstts = cstts.reshape((15, 2))
					cstts = [list(a) for a in cstts]
					# Numbers of inside blocks and outside blocks
					inside_ct = int(str(fs.get_line()))
					outside_ct = int(str(fs.get_line()))
					# Then retrieve the strings representing the blocks
					is_blocks = []
					os_blocks = []
					for i in range(inside_ct):
						is_blocks.append(eval(str(fs.get_line())))
					for i in range(outside_ct):
						# Remove redundancy: inside blocks shouldn't also be outside
						# blocks. How does this even happen?
						osb = eval(str(fs.get_line()))
						#						in_isb = False
						#						for j in range(inside_ct):
						#							if np.all(np.array(is_blocks[j]) - np.array(osb) == 0):
						#								in_isb = True
						#								continue
						os_blocks.append(osb)
					for m, n in transformations:
						ch_c_live = self.possible_centers_live[self.possible_centers.index(ch_c)]
						ch_c_live = m.dot(ch_c_live)
						t_ch_c = str(ch_c_live)
						t_cstts = n.dot(cstts)
						t_is_blocks = m.dot(np.array(is_blocks).T).T.tolist()
						t_os_blocks = m.dot(np.array(os_blocks).T).T.tolist()

						constraint_string = str((ch_c_live, t_cstts))
						if constraint_string not in all_sorted_constraints:
							all_constraints.append(t_cstts.tolist())
							constraints_sorted[t_ch_c].append(t_cstts.tolist())
							all_sorted_constraints.append(str((ch_c_live, t_cstts.tolist())))
							all_chunks.append(str((ch_c_live, t_is_blocks, t_os_blocks)))
							all_blocks.append((t_is_blocks, t_os_blocks))
							all_chosen_centers.append(t_ch_c)
							for block in t_is_blocks:
								all_block_axes.append(str(block - np.floor(block)))
						else:
							dupecounter += 1
							print("Found duplicate under rotation " + m)
					print("Loading chunklayouts..." + str(
						round(100 * sum([len(x) for x in constraints_sorted.values()]) / 5000)) + "%")
			except Exception as e:
				print("Encountered some sort of problem loading.")
				traceback.print_exc()
			fs.close()
		# print("Duplicates due to symmetry: "+str(dupecounter))
		print("Constraint counts for each possible chunk: " + str([len(x) for x in constraints_sorted.values()]))

		# Save file in a faster to load format
		#		fs.open("res://temp_test",fs.WRITE)
		#		fs.store_line(repr(all_constraints).replace('\n',''))
		#		fs.store_line(repr(constraints_sorted).replace('\n',''))
		#		fs.store_line(repr(all_blocks).replace('\n',''))
		#		fs.store_line(repr(all_chosen_centers).replace('\n',''))
		#		fs.close()

		possible_blocks = set()
		for blocklayout in all_blocks:
			combined = np.concatenate([blocklayout[0], blocklayout[1]])
			combined = combined * 2
			combined = np.array(np.round(combined), dtype=np.int64) / 2
			combined = [repr(list(x)) for x in combined]
			for block in combined:
				possible_blocks.add(block)
		blocklist = [eval(x) for x in possible_blocks]

		inside_bool = np.zeros((len(all_blocks), len(blocklist)), dtype=np.bool)
		outside_bool = np.zeros((len(all_blocks), len(blocklist)), dtype=np.bool)
		for i in range(len(all_blocks)):
			inside_bool[i] = np.any(
				np.all(np.repeat(all_blocks[i][0], len(blocklist), axis=0).reshape(-1, len(blocklist), 6)
					   - np.array(blocklist) == 0, axis=2).T, axis=1)
			outside_bool[i] = np.any(
				np.all(np.repeat(all_blocks[i][1], len(blocklist), axis=0).reshape(-1, len(blocklist), 6)
					   - np.array(blocklist) == 0, axis=2).T, axis=1)
			#			for j in range(len(blocklist)):
			#				inside_bool[i,j] = np.any(np.all(np.array(all_blocks[i][0])-np.array(blocklist[j])==0,axis=1))
			#				outside_bool[i,j] = np.any(np.all(np.array(all_blocks[i][1])-np.array(blocklist[j])==0,axis=1))
			print("Computing booleans..." + str(round(100 * i / len(all_blocks))) + "%")
		fs.open("res://temp_test", fs.WRITE)
		fs.store_line(repr((all_constraints).tolist()).replace('\n', ''))
		fs.store_line(repr((all_chosen_centers).tolist()).replace('\n', ''))
		fs.store_line(repr(blocklist).replace('\n', ''))
		fs.close()
		np.save("temp_test_is", inside_bool, allow_pickle=False)
		np.save("temp_test_os", outside_bool, allow_pickle=False)

	def save_templates_npy(self, filename="templates_dump"):
		"""
		Saves the current list of constraints in the three-file npy format.
		"""
		inside_bool = np.zeros((len(self.all_blocks), len(self.blocklist)), dtype=np.bool)
		outside_bool = np.zeros((len(self.all_blocks), len(self.blocklist)), dtype=np.bool)
		for i in range(len(self.all_blocks)):
			inside_bool[i] = np.any(np.all(np.repeat(self.all_blocks[i][0],
													 len(self.blocklist), axis=0).reshape(-1, len(self.blocklist), 6)
										   - np.array(self.blocklist) == 0, axis=2).T, axis=1)
			outside_bool[i] = np.any(np.all(np.repeat(self.all_blocks[i][1],
													  len(self.blocklist), axis=0).reshape(-1, len(self.blocklist), 6)
											- np.array(self.blocklist) == 0, axis=2).T, axis=1)
			print("Computing booleans..." + str(round(100 * i / len(self.all_blocks))) + "%")
		fs = File()
		fs.open("res://" + filename, fs.WRITE)
		# The data can sometimes vary between ndarrays and lists, depending on
		# what format it was loaded from, whether it was freshly processed/compactified,
		# etc.
		if type(self.all_constraints) == type(np.arange(1)):
			fs.store_line(repr((self.all_constraints.tolist())).replace('\n', ''))
		else:
			if type(self.all_constraints[0]) == type(np.arange(1)):
				fs.store_line(repr([constrt.tolist() for constrt in self.all_constraints]).replace('\n', ''))
			else:
				fs.store_line(repr(self.all_constraints).replace('\n', ''))
		if type(self.all_chosen_centers) == type(np.arange(1)):
			fs.store_line(repr((self.all_chosen_centers).tolist()).replace('\n', ''))
		else:
			if type(self.all_chosen_centers[0]) == type(np.arange(1)):
				fs.store_line(repr([center.tolist() for center in self.all_chosen_centers].replace('\n', '')))
			else:
				fs.store_line(repr(self.all_chosen_centers).replace('\n', ''))
		if type(self.blocklist) == type(np.arange(1)):
			fs.store_line(repr(self.blocklist.tolist()))
		else:
			if type(self.blocklist[0]) == type(np.arange(1)):
				fs.store_line(repr([block.tolist() for block in self.blocklist]).replace('\n', ''))
			else:
				fs.store_line(repr(self.blocklist))
		fs.close()
		np.save(filename + "_is", inside_bool, allow_pickle=False)
		np.save(filename + "_os", outside_bool, allow_pickle=False)

	def load_templates_npy(self, filename="simplified_constraints"):  # was "temp_test" for a long time
		# TODO Definitely need tests that repeated saving and loading produces identical files. I don't want to change
		#  something here to fix a bug only to find that it's just a particular file that was odd.
		fs = File()
		fs.open("res://" + filename, fs.READ)
		self.all_constraints = eval(str(fs.get_line()))
		# NOTE Chosen centers are stored as strings!
		self.all_chosen_centers = eval(str(fs.get_line()))
		self.blocklist = np.array(eval(str(fs.get_line())))
		fs.close()
		self.inside_blocks_bools = np.load(filename + "_is.npy")
		self.outside_blocks_bools = np.load(filename + "_os.npy")
		for i in range(self.inside_blocks_bools.shape[0]):
			self.all_blocks.append((self.blocklist[self.inside_blocks_bools[i]], self.blocklist[self.outside_blocks_bools[i]]))

	def load_templates_repr(self):
		starttime = time.perf_counter()
		fs = File()
		fs.open("res://chunk_layouts.repr", fs.READ)
		self.all_constraints = eval(str(fs.get_line()))
		print("Loaded part 1")
		print(time.perf_counter() - starttime)
		self.constraints_sorted = eval(str(fs.get_line()))
		print("Loaded part 2")
		print(time.perf_counter() - starttime)
		self.all_blocks = eval(str(fs.get_line()))
		print("Loaded part 3")
		print(time.perf_counter() - starttime)
		self.all_chosen_centers = eval(str(fs.get_line()))
		print("Loaded part 4")
		print(time.perf_counter() - starttime)
		fs.close()

	def simplify_constraints(self, no_new_values=True):
		"""
		The original generated constraints in self.all_constraints (as created by
		numpylattice.py) are very broad in some directions, sometimes spanning most
		of the space despite the small size of the actual constrained region (ie,
		other dimensions are doing most of the work). This function moves constraints
		inwards, closer to the actual region, so that some other processes can be
		faster.

		The new constraints are simply placed in self.all_constraints, and
		self.constraint_nums is updated accordingly.

		If no_new_values is True, this function will guarantee that the new
		self.constraint_nums is not larger than the old one, at a cost to
		constraint snugness.
		"""
		# We want to simplify the constraints. Many span more than half of one
		# of their 15 dimensions, but those values aren't actually relevant in
		# the 3D constraint space
		# because some of the other dimensions are pinned down to a range of
		# 1 or 2 constraint_nums values. So we want to see what values are actually
		# realizable, and collapse these large ranges down.
		self.all_simplified = []
		for i in range(len(self.all_constraints)):
			# print( [self.constraint_nums[dim].index(np.array(self.all_constraints[i])[dim,1])
			#				- self.constraint_nums[dim].index(np.array(self.all_constraints[i])[dim,0]) for dim in range(15)] )
			# To figure out what's relevant, we acquire a point inside the constraints
			# and re-base them as distance from that point. (This would have been easier
			# done when they were first created, since they were originally generated
			# as relative distance like this.)
			# (This step adds about 40 seconds)
			self.original_seed = np.array([r.random(), r.random(), r.random(), r.random(), r.random(), r.random()])
			self.make_seed_within_constraints(self.all_constraints[i])
			translated_constraints = (np.array(self.all_constraints[i]).T - np.array(self.twoface_normals).dot(
				self.original_seed.dot(self.normallel.T))).T

			# Sort all 30 constraints by how distant they are from this point.
			fields = [('tc', np.float), ('index', np.int), ('dir', np.int)]
			aug_tc = ([(np.abs(translated_constraints[j][0]), j, -1) for j in range(15)]
					  + [(np.abs(translated_constraints[j][1]), j, 1) for j in range(15)])
			sorted_tc = np.sort(np.array(aug_tc, dtype=fields), order='tc')

			# We're going to need two small margins to try and avoid floating point errors;
			# the second one very slightly bigger than the first. These of course limit how
			# snug our constraints will become. Larger margins also slow down the snugging process.
			margin1 = 0.00000000000001
			margin2 = 0.000000000000011
			# TODO Generating all the corners would enable very snug
			#  constraints, and speed up the constraint search by a bit.
			#  (I'm uncertain now whether it's very much.)
			# One direction might be to store, alongside each corner, information about which
			# plane intersections generated it. That way, another plane which cuts that corner
			# off knows which planes to use to generate new corners, and check whether those
			# corners are really part of the shape.
			corners = []
			# First we generate all corners between constraint planes.

			# Choosing the first 6 planes guarantees some intersections.
			closest_six = set()
			for cst in sorted_tc:
				closest_six.add(cst['index'])
				if len(closest_six) >= 6:
					break
			closest_six = list(closest_six)
			for index_i in range(6):
				for index_j in range(index_i, 6):
					for index_k in range(index_j, 6):
						plane_i = closest_six[index_i]
						plane_j = closest_six[index_j]
						plane_k = closest_six[index_k]
						basis_matrix = np.array([self.twoface_normals[plane_i], self.twoface_normals[plane_j],
												 self.twoface_normals[plane_k]])
						# Not all planes work together. (Even if distinct, some never meet in a corner.)
						if np.linalg.det(basis_matrix) != 0.0:
							for dirspec in [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0),
											(1, 1, 1)]:
								new_corner = np.linalg.solve(basis_matrix,
															 [self.all_constraints[i][plane_i][dirspec[0]],
															  self.all_constraints[i][plane_j][dirspec[1]],
															  self.all_constraints[i][plane_k][dirspec[2]]])
								corners.append(new_corner)

			# Then we throw out all corners which fall outside the constraint
			# region, leaving only actual corners.
			# NOTE This has been altered to only use planes in "closest_six"
			# for its checks, rather than genuinely discarding all exterior points,
			# which only works if we successfully generated them all.
			for cst in sorted_tc:
				if cst['index'] in closest_six:
					# Get all corners' magnitude along this direction.
					# print(len(corners))
					corner_dots = [corner.dot(self.twoface_normals[cst['index']]) for corner in corners]

					if cst['dir'] == 1:
						if self.all_constraints[i][cst['index']][1] < max(corner_dots):
							# Constraint plane falls inside corners; we need to
							# remove some corners.

							# We need to be careful about floating point error here. Don't delete
							# corners which are just barely outside.
							smaller_corners_list = [corners[index] for index in range(len(corners))
													if corner_dots[index] <= self.all_constraints[i][cst['index']][
														1] + margin1]
							corners = smaller_corners_list
					else:
						# So, this is the case cst['dir'] == -1
						if self.all_constraints[i][cst['index']][0] > min(corner_dots):
							# Constraint plane falls inside corners; some corners not relevant.

							smaller_corners_list = [corners[index] for index in range(len(corners))
													if corner_dots[index] >= self.all_constraints[i][cst['index']][
														0] - margin1]
							corners = smaller_corners_list

			# Finally, we snug up all constraints to lie near these corners.
			snugged = np.array(self.all_constraints[i])
			for cst in sorted_tc:
				# Check all corners' magnitude in this direction
				corner_dots = np.sort([corner.dot(self.twoface_normals[cst['index']]) for corner in corners])

				# Is the seed inside the corners?
				seed_dot = self.original_seed.dot(self.normallel.T).dot(self.twoface_normals[cst['index']])
				if seed_dot > corner_dots[-1] or seed_dot < corner_dots[0]:
					print("\t\t\tSEED OUTSIDE ITS BOX")
					raise Exception("Seed outside its box; " + str(seed_dot) + " not between " + str(
						corner_dots[0]) + " and " + str(corner_dots[-1]) + "."
									+ "\n Actual constraint was from " + str(self.all_constraints[i][cst['index']][0])
									+ " to " + str(self.all_constraints[i][cst['index']][1]) + ".")

				# Want to use the lowest constraint_num beyond our highest corner.
				nums = np.array(self.constraint_nums[cst['index']])

				if cst['dir'] == 1:
					if self.all_constraints[i][cst['index']][1] > max(corner_dots):
						if no_new_values:
							# This direction doesn't affect the overall constraint. Can
							# we bring it closer?
							smallest = snugged[cst['index']][1]
							for f in range(len(nums)):
								if nums[f] >= max(corner_dots):
									smallest = nums[f]
									break
							snugged[cst['index']][1] = smallest
						else:
							# We must be careful about floating point error. If the corner we're
							# snugging up to lies very slightly inside the constraint region,
							# we may add a tiny facet.
							# TODO Certainly this could be a bit cleaner. Perhaps test the corner
							#  to see if we can use its literal value.
							snugged[cst['index']][1] = min(max(corner_dots) + margin1,
														   self.all_constraints[i][cst['index']][1])
					else:
						# This indicates a constraint plane falling inside the
						# corners, which can't happen if we've chosen the true
						# corners. If the amount is greater than reasonable
						# floating point error, something has gone wrong.
						if self.all_constraints[i][cst['index']][1] - max(corner_dots) > margin2:
							raise Exception("A corner has been incorrectly included in constraint simplification.")
				if cst['dir'] == -1:
					smallest = snugged[cst['index']][0]
					if self.all_constraints[i][cst['index']][0] < min(corner_dots):
						if no_new_values:
							# Search for suitable member of nums
							for f in range(len(nums) - 1, -1, -1):
								if nums[f] <= min(corner_dots):
									smallest = nums[f]
									break
							snugged[cst['index']][0] = smallest
						else:
							# Maximal snugness save cautious margin
							snugged[cst['index']][0] = max(min(corner_dots) - margin1,
														   self.all_constraints[i][cst['index']][0])
					else:
						if self.all_constraints[i][cst['index']][0] - min(corner_dots) < -margin2:
							raise Exception("A corner has been incorrectly included in constraint simplification.")
				# smallest = cst['dir']*max(cst['dir']*nums[cst['dir']*nums >= cst['dir']*corner_dots[-1*cst['dir']]])

				if not self.satisfies_by(self.original_seed, snugged) > 0:
					print(str(cst['dir']) + " Seed got excluded")
					raise Exception(str(cst['dir']) + " Seed got excluded")
				if (self.all_constraints[i][cst['index']][1] - self.all_constraints[i][cst['index']][0]
						< snugged[cst['index']][1] - snugged[cst['index']][0]):
					print(str(cst['dir']) + "Somehow made constraint wider")
			self.all_simplified.append(snugged)

		#			print("Simplified comparison:")
		#			print(self.satisfies_by(self.original_seed,self.all_constraints[i]))
		#			print(self.satisfies_by(self.original_seed,self.all_simplified[i]))
		print("Length of simplified constraints:")
		print(len(self.all_simplified))

		self.simplified_constraint_nums = [set(), set(), set(), set(), set(), set(), set(), set(), set(), set(),
										   set(), set(), set(), set(), set()]
		for i in range(len(self.all_simplified)):
			for j in range(15):
				self.simplified_constraint_nums[j] = self.simplified_constraint_nums[j].union(
					set(self.all_simplified[i][j]))
		for i in range(15):
			sorted = list(self.simplified_constraint_nums[i])
			sorted.sort()
			self.simplified_constraint_nums[i] = sorted
		print("Number of constraint planes before simplification:")
		print(sum([len(nums) for nums in self.constraint_nums]))
		print("Number of constraint planes after simplification:")
		print(sum([len(nums) for nums in self.simplified_constraint_nums]))
		print([len(dimnums) for dimnums in self.simplified_constraint_nums])

		self.all_constraints = self.all_simplified
		self.constraint_nums = self.simplified_constraint_nums

	def draw_block_wireframe(self, block, st, multiplier):
		face_origin = np.floor(block).dot(self.worldplane.T) * multiplier
		face_tip = np.ceil(block).dot(self.worldplane.T) * multiplier
		dir1, dir2, dir3 = np.eye(6)[np.nonzero(np.ceil(block) - np.floor(block))[0]].dot(
			self.worldplane.T) * multiplier
		corner1, corner2, corner3, corner4, corner5, corner6, corner7, corner8 = (
			face_origin, face_tip, face_origin + dir1, face_origin + dir2, face_origin + dir3,
			face_tip - dir1, face_tip - dir2, face_tip - dir3
		)
		dir1 = Vector3(dir1[0], dir1[1], dir1[2])
		dir2 = Vector3(dir2[0], dir2[1], dir2[2])
		dir3 = Vector3(dir3[0], dir3[1], dir3[2])
		# Draw by recombining
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2)

	def draw_block(self, block, st, multiplier):
		face_origin = np.floor(block).dot(self.worldplane.T) * multiplier
		face_tip = np.ceil(block).dot(self.worldplane.T) * multiplier
		dir1, dir2, dir3 = np.eye(6)[np.nonzero(np.ceil(block) - np.floor(block))[0]].dot(
			self.worldplane.T) * multiplier
		# Make "right hand rule" apply
		if np.cross(dir1, dir2).dot(dir3) < 0:
			_ = dir1
			dir1 = dir2
			dir2 = _
		corner1, corner2, corner3, corner4, corner5, corner6, corner7, corner8 = (
			face_origin, face_tip, face_origin + dir1, face_origin + dir2, face_origin + dir3,
			face_tip - dir1, face_tip - dir2, face_tip - dir3
		)
		dir1 = Vector3(dir1[0], dir1[1], dir1[2])
		dir2 = Vector3(dir2[0], dir2[1], dir2[2])
		dir3 = Vector3(dir3[0], dir3[1], dir3[2])
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1 + dir2)

		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1 + dir2)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2)

		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2 + dir3)

		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir2 + dir3)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3)

		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3 + dir1)

		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]))
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir3 + dir1)
		st.add_vertex(Vector3(face_origin[0], face_origin[1], face_origin[2]) + dir1)

		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1 - dir2)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1)

		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1 - dir2)

		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2 - dir3)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2)

		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir2 - dir3)

		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3 - dir1)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3)

		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]))
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir1)
		st.add_vertex(Vector3(face_tip[0], face_tip[1], face_tip[2]) - dir3 - dir1)

	def make_seed_within_constraints(self, constraints):
		upper_limit = 10000
		counter = 0
		while counter < upper_limit and not self.satisfies(self.original_seed, constraints, strict=True):
			counter += 1
			axes = list(range(15))
			r.shuffle(axes)
			for axis in axes:
				proj_seed = self.original_seed.dot(self.normallel.T).dot(self.twoface_normals[axis])
				if proj_seed <= np.array(constraints)[axis, 0] or proj_seed >= np.array(constraints)[axis, 1]:
					self.original_seed -= proj_seed * self.twoface_normals[axis].dot(self.normallel)
					new_dist = r.random()
					self.original_seed += ((1 - new_dist) * np.array(constraints)[axis, 0] * self.twoface_normals[axis].dot(
						self.normallel)
								  + new_dist * np.array(constraints)[axis, 1] * self.twoface_normals[axis].dot(
								self.normallel))
				if self.satisfies(self.original_seed, constraints, strict=True):
					# Stop before we ruin it
					break
		if counter >= upper_limit:
			raise Exception("Exceeded allowed tries while trying to satisfy constraints " + str(constraints))

	def satisfies(self, vector, constraints, strict=False):
		"""
		Returns True if the vector (array or ndarray, 3D or 6D)	falls inside the
		constraints. A 6D vector is first projected into the 3D 'parallel space'.
		Constraints should be of shape (15,2), representing first a lower and then
		an upper bound in the 15 directions perpendicular to the faces of a
		triacontahedron, in the ordering represented by self.twoface_normals.
		If strict is set False, the vector may lie on the boundary; otherwise,
		vectors on the boundary result in a return value of False.
		"""
		threevector = np.zeros(3)
		if vector.shape[-1] == 6:
			threevector = vector.dot(self.normallel.T)
		if vector.shape[-1] == 3:
			threevector = vector
		if strict:
			return (np.all(self.twoface_normals.dot(threevector)
						   > np.array(constraints)[:, 0])
					and np.all(self.twoface_normals.dot(threevector)
							   < np.array(constraints)[:, 1]))
		return (np.all(self.twoface_normals.dot(threevector)
					   >= np.array(constraints)[:, 0])
				and np.all(self.twoface_normals.dot(threevector)
						   <= np.array(constraints)[:, 1]))

	def satisfies_by(self, vector, constraints):
		"""
		Returns the margin by which the vector (array or ndarray, 3D or 6D)
		falls inside the constraints. A 6D vector is first projected into the 3D
		'parallel space'. If vector is within the constraints, return value is
		positive, and represents the distance the vector would have to be moved
		to exit the constraints. If vector is outside the constraints, the
		return value is negative, and represents the distance the vector would
		have to be moved to satisfy whicever constraint it is furthest from
		satisfying. This can be somewhat smaller than the distance it would
		need to move to actually satisfy the constraint.
		Constraints should be of shape (15,2), representing first a lower and then
		an upper bound in the 15 directions perpendicular to the faces of a
		triacontahedron, in the ordering represented by self.twoface_normals.
		"""
		threevector = np.zeros(3)
		if vector.shape[-1] == 6:
			threevector = vector.dot(self.normallel.T)
		if vector.shape[-1] == 3:
			threevector = vector
		return min(np.min(self.twoface_normals.dot(threevector) - np.array(constraints)[:, 0]),
				   np.min(-self.twoface_normals.dot(threevector) + np.array(constraints)[:, 1]))

	def get_seed(self, level=1):
		"""
		Manages the world seed, so that it can be stored in increasingly accurate form over time.
		:param level: Desired chunk evel for seed to be represented on.
		:return: The world seed, as a six element ndarray.
		"""
		highest_level = self.highest_chunk.level
		seed = self.highest_chunk.seed
		# Have to subtract 1 from highest_level because... standard stored offsets are always 1 level lower than the
		# Chunk object that stores them.
		offset = self.highest_chunk.get_offset(highest_level-1)
		# print("Converting from "+str(highest_level)+" to "+str(level)+".")
		# print("Seed at highest level: ")
		# print(seed)
		# print("Offset at highest level:")
		# print(offset)
		lowered_seed = seed*pow(-1,highest_level-level)*self.phipow(-3*(highest_level-level))
		lowered_offset = np.array(np.round(offset), dtype='int64').dot(self.custom_pow(np.array(self.deflation_face_axes, dtype='int64').T, highest_level-level))
		# print("Lowered Seed w/o offset:")
		# print(lowered_seed)
		# print("Lowered offset w/o seed:")
		# print(lowered_offset)
		return lowered_offset.dot(self.squarallel) + lowered_seed

	def generate_parents(self, template_index, offset, level=1):
		"""
		Takes a chunk template (as an index into self.all_blocks etc) and the
		offset at which the chunk's relative origin sits, and returns at least
		one valid superchunk for that chunk given the current seed. Return
		value is a list of tuples (index, offset, seed) indicating each superchunk's
		template along with where its own origin will belong, and the rescaled seed
		used. Note, the returned offsets are scaled as if the child chunk were a single
		block, and should be scaled up in order to be drawn etc.
		'level' specifies the level of the chunk being handed to us; the returned
		chunk will be one level higher. Level '0' represents blocks, '1'
		represents the first chunks, etc. The effect of the level parameter is
		to map self.seed to an equivalent value for level + 1, before performing
		the search; the 'offset' is mapped up one level regardless of the given
		'level', being assumed to give coordinates of the given chunk in terms
		of blocks.
		"""
		chosen_center = self.chunk_center_lookup(template_index)
		ch3_member = np.ceil(chosen_center) - np.floor(chosen_center)

		# (Keeping all the rambly figuring-things-out comments for now)

		# We want to choose the chunk whose voxels could all have fit into the
		# original grid *as chunks* - meaning we want to choose the chunk whose
		# points are all within the tighter chunk-level constraints, IE,
		# constraints nearer to the world-plane by phi^3.
		#
		# Does that mean we could just divide the constraints by phi^3? Well,
		# what the constraints accompanying a chunk mean is that if the seed
		# falls between those constraint values, then all the points listed will
		# be present within a grid with that seed. What it would mean to be present
		# "as chunks" depends on a chosen transformation between the block scale
		# and the chunk scale -- the literal blocks aren't present "as chunks" since
		# they're at the wrong scale. We just mean that they would correspond
		# to chunks within the (tighter) chunk constraint distance, under an
		# appropriate transformation.
		# Under such a transformation, then, each point would first of all be
		# brought closer to the worldplane by a ratio of phi^3, since, that's
		# the defining feature of chunks. It seems to me the constraints *do*
		# simply shrink by phi^3 as well. I guess there's some question as to
		# whether perhaps a rotation is forced.
		# Two things worth noting: we have to move the offset (and indeed, the
		# entire worldplane) by the same transformation, and generally we need
		# to consider translations; because although I suppose there must be
		# choices of offset which place the origin on the appropriate corner of
		# the new superchunk, that won't generally mean that it's also on the
		# corner of the old chunk - meaning that a translated version of the old
		# seed is what needs to be tested against the new constraints, or vice
		# versa.

		# We need to calculate the chunk axes inverse carefully. When Numpy takes a matrix inverse, it makes it
		# out of floats, and floating point error turns it into junk at around the 13th or 14th power (IE, chunks of
		# level 13 or 14).
		# What we'd like is this simple line:
		# chunk_axes_inv = np.round(np.linalg.matrix_power(np.array(self.deflation_face_axes,dtype=int).T, -level))

		# But we'll break it into smaller steps:
		# TODO The below method creates a hang of about a second if chunk level gets near 1 million. If I pre-calculate
		#  just a few powers of deflation_face_axes, e.g. 10, 100, 1000, 10,000, etc, these very rare hiccups could
		#  be avoided.
		def_face_matrix = np.array(self.deflation_face_axes, dtype='int64').T
		# Testing has shown problems cropping up when below increment is equal to 9. Using 7 for safety margin.
		chunk_axes_inv = self.custom_pow(def_face_matrix, -level, safe_amount=7)
		level_sign = pow(-1, level)

		# Does this seed fall within our constraint region?
		# Seeds are equivalent under integer addition and subtraction, but
		# I'm not sure what shape our constraint space takes, particularly once
		# we include all the translations - IE, for each chunk layout, we slide
		# the constraints over in accordance with each valid block, when checking
		# whether the layout is a valid superchunk. It does seem that the translations
		# don't overlap with one another, and I expect that they share edges and fill
		# some space, but I don't know what shape it turns out to be for sure.
		# If everything is working fine, it has volume 1 and would capture any
		# possible seed if it were translated by all the 6D basis vectors; but
		# I need to restrict the seeds to fall inside it, meaning I need to
		# preemptively perform the translation. Right now, seeds are initialized
		# to a random position inside the chosen chunk orientation's constraints,
		# so "chunk_axes_inv_seed" should fall within the constraints for a
		# correspondingly-shaped block existing at the 3D origin. I guess the
		# question is, would all template constraints compatible with that block's
		# presence overlap it (falling within it exactly for seed values where the
		# block is actually present)? When the block is literally present in them,
		# the answer is yes since those constraints are being calculated the same
		# way.
		# I guess I'm thinking of this a bit wrong - adding, say, (1,1,1,0,0,0) to
		# the seed doesn't affect the appearance of the grid, but it affects the
		# 6D coordinates of every block present. Constraints for a specific block's
		# presence or absence are absolute, rather than determined up to translation.
		# The "rescaling" transformation above, combined with all the translations
		# of the seed occurring in the search below, check the seed absolutely
		# for presence of the specific blocks in the templates.

		# Nonetheless: successive applications of the chunk transformation make
		# our seed further and further from the origin. What's happening can be
		# pictured as: we start with an origin which is not a superchunk corner,
		# not a supersuperchunk corner, not a supersupersuperchunk corner, etc. -
		# so if we repeatedly convert the seed to more-and-more-super coordinates,
		# it eventually falls outside the constraints, representative of the fact
		# that our origin point is not in the lattice on this level. At such a
		# point, it no longer makes sense to translate the seed by the current
		# level's integer lattice, to check whether a point is sufficiently
		# near the worldplane.

		# So we need a process where we carefully step up the levels. Whenever
		# we find that a step leaves us measuring the seed from a point which
		# is no longer close enough to the worldplane be included, we need to
		# switch to a nearby point which *is* included. The way in which this
		# is navigated undoubtedly will affect how much floating point error
		# is accumulated.

		# TODO figure out what the best way of minimizing floating point error is.
		#  - I found it was important to do the dot products before the addition (in calculating safer_seed), since
		#    lowered_offset can be a very large number and the seed is a small one; the dot product brings them
		#    into something like a shared range. Especially important since their difference, safer_seed, is supposed
		#    to be quite tiny.
		#  - I found that much floating point error was being created by the matrix power, used to calculate chunk_axes_inv.
		#    So I wrote my own matrix power function, which has been somewhat carefully tested.
		#  - The chunk axis transform is simply a scaling up in the worldplane and simultaneous scaling down in "parallel
		#    space". Maybe it can be calculated with less problems in those terms. Instead of multiplying offset by a matrix
		#    power, multiply it by a power of phi and then add it to the seed, then take the squarallel of that.
		#  - UNUSED THOUGHT The "offset" of higher-level chunks gets huge; their transformed axes are squashed closer
		#    and closer to the worldplane, so that the origin is extremely far away. This means even without floating
		#    point error, there would be a problem when the offsets exceed what could be stored by a long int. However,
		#    the level 0 offset (position in block coordinates) will always be reasonably small integers, since corners
		#    of chunks are always on blocks, and, the player will not travel so many block-lengths as to max out long
		#    ints. Probably, I should be storing level-0 offsets for all chunks.
		#    Similarly. the "seed" when rescaled to that extreme necessarily becomes very inaccurate due to distance
		#    from origin. But we don't need to know those very large numbers; all that matters for the high-up chunks is
		#    the stuff after the decimal point, IE, how far the seed is from the chunk corner. So if we were trying to
		#    move the seed upwards right away, we could do the matrix multiplication a couple levels at a time, and
		#    repeatedly check whether the seed coordinates were of absolute value less than 1; and, if not, put them
		#    there. This simplification is what's accomplished (possibly more elegantly) below by subtracting the
		#    lowered_offset from the seed. However: at higher and higher levels, lowered_offset simply becomes a better
		#    and better approximation of the seed, so clearly it's storing some unnecessary information. What we
		#    ultimately wish to know is its difference from the seed. So the only way to discard unnecessary info right
		#    away, would be to bring the seed up to the right level first; which is what we were trying to avoid. It's
		#    sounding like the most accurate approach is to move the seed upwards step by step like I described.


		# "offset" starts out at the level "level", and the seed starts out at
		# level 1, so we want to apply deflation_face_axes level-1 times.
		# lowered_offset = np.linalg.matrix_power(np.array(self.deflation_face_axes,dtype=int), (level - 1)).dot(np.round(offset))
		# lowered_offset = np.array(np.round(offset), dtype=int).dot(self.custom_pow(def_face_matrix, level - 1))
		# But we know "offset" is extremely close to the worldplane, and all that matters to us is its distance from worldplane.
		# Can we discard useless info (and thus store more accuracy) by dotting it with squarallel right away?
		lowered_offset = np.array(np.round(offset), dtype='int64').dot(self.custom_pow(def_face_matrix, level - 1))
		# Can we get less floating point problems by just multiplying by a power of phi?
		# NO: def_face_matrix is integer, so the above way is exact.
		#lowered_offset = -level_sign*np.array(offset,dtype=int)*self.phipow(-3*(level-1))

		# lowered_offset contains redundant information, since it represents a position extremely close to the
		# worldplane. Before we dot it with squarallel, we want to reduce that redundant information as much as we can.
		# Mathematically, we would like to add and subtract basis elements of the worldplane itself, in order to get
		# lowered_offset very close in value to the seed. However, the worldplane's basis contains phi, so it's not
		# stored exactly, and we would be introducing little bits of error with each addition and subtraction. This step
		# could be done correctly if I had the golden_field class working... is there a makeshift solution that would
		# get some of the benefits?

		# approx_coefficients = np.array(np.round((self.worldplane / np.linalg.norm(self.worldplane[0])).dot(lowered_offset)
		# 										/ np.linalg.norm(self.worldplane[0])),dtype='int64')
		# worldplane_12d = np.array(
		# 	[[0,0,1,0,0,-1,
		# 	  1,0,0,1,0,0],
		# 	 [1,0,0,-1,0,0,
		# 	  0,1,0,0,1,0],
		# 	 [0,1,0,0,-1,0,
		# 	  0,0,1,0,0,1]],dtype='int64')
		# approx_gf = approx_coefficients.dot(worldplane_12d)
		# Oh... because of the way the worldplane is set up, each entry will just be a sum of one integer field and one phi field.
		# IE, the only benefit I'm getting here is I can do the purely integer arithmetic before I do the floating point part.
		# Accuracy is lost, in each dimension, proportional to the inaccuracy in each large multiple of phi.
		# safer_lowered_offset = lowered_offset - approx_gf[:6]
		# safer_lowered_offset = safer_lowered_offset - self.phi*approx_gf[6:]
		# Note: This seems to be the first weak point, currently. When offset coordinates are more than 17 digits long,
		# converting them to float at all creates problems. (These problems somehow *don't* lead to a crash.)
		# print(safer_lowered_offset)

		# To reduce floating point error, we separately dot "seed" and "lowered_offset" with squarallel, then subtract.
		# But, "seed" doesn't actually need projected, it's already been.
		# Taking the squarallel theoretically slides the chunk's origin onto the line between 6D origin and seed. Since
		# chunks are highly flattened to the worldplane, this puts the chunk origin extremely close to the seed itself,
		# giving an extremely number -- which protects us from floating point error when we scale up (via multiplying
		# by powers of phi).
		# (Encountered pretty big floating point errors around 1e-9, or, level-13 chunks.)
		# (Update: since introducing get_seed(), floating point errors become *visible* around 1e-9, IE, the printed
		# numbers differ by their least significant digit. "safer-seed" fails to become smaller after that, staying
		# about 1e-9 even at higher levels. But safer-seed isn't actually used, and things remain reasonable until
		# level 17. Even after level 17, the seed becomes unreasonable but nothing crashes.
		# safer_seed = self.get_seed() - safer_lowered_offset.dot(self.squarallel)
		# chunk_axes_inv_seed = chunk_axes_inv.dot(safer_seed)
		# Can we get less floating point problems by just multiplying by a power of phi?
		# chunk_axes_inv_seed_2 = level_sign * safer_seed * self.phipow(3 * level)
		# The two are added together due to a hidden -1 multiplication as offset gets raised an extra level
		# chunk_axes_inv_seed_3 = level_sign * self.phipow(3 * level) * self.get_seed() + self.phipow(3) * np.array(offset,
		# 																								  dtype='int64')  # .dot(self.squarallel)
		# TODO The below is about as direct as we might hope for, but, we're taking offset (which might be a huge
		#  integer) and converting it to a float. Only way around this I've thought of: each new highest-level chunk is
		#  considered a new origin for the sake of offsets that level and above. This significantly complicates offset
		#  calculations but keeps them about the same size on each level.
		chunk_axes_inv_seed = self.get_seed(level+1) + self.phipow(3)*np.array(offset,dtype='int64').dot(self.squarallel)

		print("Calculating seed from safe point " + str(lowered_offset))
		print(str(lowered_offset.dot(self.squarallel)))
		#print(str(-level_sign * np.array(offset, dtype=int).dot(self.squarallel) * self.phipow(-3 * (level - 1))))
		# print("Translated seed (should be < " + "{:.1e}".format(math.pow(1 / 4.7, level)) + "):" + str(safer_seed))
		# print("Translated Seed: " + str(
		# 	self.get_seed( + level_sign * np.array(offset, dtype=int).dot(self.squarallel) * self.phipow(-3 * (level - 1))))
		print("Rescaled seed: " + str(chunk_axes_inv_seed))
		# print("Rescaled safer seed: " + str(chunk_axes_inv_seed_2))
		# print("Rescaled seed: " + str(chunk_axes_inv_seed_3))
		print("Current seed:")
		print(self.get_seed())
		print("Original seed:")
		print(self.original_seed)
		# print("Directly rescaled: "+ str(-safer_seed*self.phipow(3*level)))

		# With the chunk and seed mapped down to block size, we can picture the old blocks present
		# as sub-blocks -- points which could be included in the grid if we widened the neighbor
		# requirements by a factor of phi cubed.

		# More importantly, there's a long-winded approach we can use to check a given chunk
		# for admissibility as a superchunk. We first choose a translation, which maps our
		# block (mapped down from a chunk) into an appropriately shaped block within the
		# chunk. Then we can reverse the scaling-down  map (so, use just the plain
		# deflation_face_axes matrix) on each point in the stored template, to get its
		# position as a potential chunk in the original grid. Then we test that point
		# under the more exacting constraints for chunk-hood. If all the points of a
		# proposed chunk + translation pass this test with our chosen offset, we've
		# found the correct superchunk. (I suppose the corners of the chunk also have
		# to qualify as superchunks, falling within even more restricted ranges.)

		# So, if we were to take those restricted chunk (and superchunk) constraintns
		# and map them backwards -- applying chunk_axes_inv -- then take their intersection,
		# would we get the saved chunk template constraints? TODO write an actual test.
		# But for now I think that's the case.

		# The upshot is, we take "chunk_axes_inv_seed" and consider all its possible
		# translations within a given chunk (which amount to new seed values). Then
		# we ask whether any of those seed values fall within the constraints for
		# the chunk. If so, this is our superchunk, and the corresponding translation
		# is our position in the superchunk. And we expect this proceduce to yield
		# a unique choice of superchunk and translation, except for the possibility
		# that we are a boundary chunk shared by several superchunks. (We also
		# suspect there must be a faster procedure than checking all the translations.)

		# I realize all of that was basically repeated from the comment block
		# before, but it's very late and writing it out helped.

		# OK, the procedure isn't identifying a single unique superchunk, but
		# I think the reason is that some blocks have their centers exactly on
		# the edges of chunks. I want to try and tweak my chunk template files
		# to fix this -- how do I do that? Systematically searching for examples
		# would consist of generating translated versions of the template
		# constraints, corresponding to each block in the chunk; then checking for
		# overlap amongst all chunks, between constraints coming from blocks
		# of the same orientation and shape. Realistically I should store all
		# the translated constraints anyway, sorted by block shape, and have some
		# fast lookup method for identifying which (template, translation) pair
		# a given offset falls within.
		# I should be able to introduce a rule for which chunk "owns" a block
		# within such a lookup method.

		# We only want to apply the matrix here once; we're assuming both
		# chunk_center and offset are already in terms of the scale one level
		# down.
		chunk_as_block_center = np.round(
			(np.array(np.round(np.linalg.inv(self.deflation_face_axes)),dtype='int64').dot(
				np.array(np.round(chosen_center*2),dtype='int64') + offset*2))) / 2.0
		# Inverse deflation face axes are integer, we just need to make the dtype right to preserve our data.
		# Oof... this goes badly wrong if we don't round it first.
		chunk_as_block_origin = np.array(np.round(np.linalg.inv(self.deflation_face_axes)),dtype='int64').dot(offset)
		print("Rescaled chunk center: " + str(chunk_as_block_center))
		print("Rescaled chunk origin: " + str(chunk_as_block_origin))

		# By using the constraint lookup tree, we can make parent generation much faster: 20 parents generate in 0.28
		# seconds rather than 19.8 seconds.

		# We can iterate over all possible blocks instead of all possible templates.
		all_is_blocks = np.array(self.is_blocklist)
		# all_aligned_blocks = all_is_blocks[np.nonzero(np.all(all_is_blocks - chunk_as_block_center
		# 														 - np.round(all_is_blocks - chunk_as_block_center) == 0,
		# 														 axis=1))[0]]
		block_shape_index = self.possible_centers.index(self.all_chosen_centers[template_index])
		aligned_blocks_is_indices = self.is_blocklist_alignment_lookup[block_shape_index]
		aligned_blocks_bool_indices = self.is_to_all_bool_lookup[aligned_blocks_is_indices]
		all_aligned_blocks = all_is_blocks[aligned_blocks_is_indices]
		# TODO I was trying to speed things up by using self.inside_blocks_bools as a look up table, but getting the
		#  indices for it was slow enough to be detrimental overall. Used to get 20 of these in .28 seconds somehow,
		#  now I've whittled it down from .58 to .43, but can't seem to find the lost .15 seconds. (... commenting out
		#  some other stuff, I'm now at 0.18 seconds total, but I swear I was at 0.23 seconds even *with* that other
		#  stuff, just a few hours ago...)
		# aligned_blocks_bool_indices = np.nonzero(np.all(np.repeat([self.blocklist],len(all_aligned_blocks),axis=0)
		# 												- np.repeat([all_aligned_blocks],len(self.blocklist),axis=1)
		# 												.reshape((len(all_aligned_blocks),len(self.blocklist),6)) == 0, axis=2))[1]
		all_block_offsets = np.floor(all_aligned_blocks)
		all_proposed_origins = -all_block_offsets
		all_translated_seeds = chunk_axes_inv_seed - all_proposed_origins.dot(self.squarallel)
		all_inside_hits = []
		for i in range(len(all_translated_seeds)):
			# find_satisfied assumes we send it valid seeds, so we need to catch errors.
			hits = np.array([],dtype='int')
			try:
				hits = np.array(self.find_satisfied(all_translated_seeds[i]),dtype=int)
			except Exception:
				pass
			real = self.inside_blocks_bools[hits,aligned_blocks_bool_indices[i]]
			real_hits = hits[real]
			#for hit in hits[self.inside_blocks_bools[hits,aligned_blocks_bool_indices[i]]]:
			if np.any(real):
					hit = real_hits[0]
				# Check if aligned block which generated the seed is actually present in this template.
				#if self.inside_blocks_bools[hit,aligned_blocks_bool_indices[i]]:
				#if np.any(np.all(np.array(self.all_blocks[hit][0]) - all_aligned_blocks[i] == 0,axis=1)):
					all_inside_hits.append((hit, all_proposed_origins[i] + chunk_as_block_origin,
									chunk_axes_inv_seed - all_proposed_origins[i].dot(self.squarallel)))
					print("Seed magnitude: "+str(np.linalg.norm(chunk_axes_inv_seed)))
					print("New seed mag: "+str(np.linalg.norm(all_inside_hits[-1][2])))
					# TODO Should skip the "return" during testing to ensure only 1 hit happens.
					return all_inside_hits
		if len(all_inside_hits) == 1:
			return all_inside_hits
		if len(all_inside_hits) > 0:
			print("find_satisfied method found "+str(len(all_inside_hits))+" hits.")
			for hit in all_inside_hits:
				print(hit)
			return [all_inside_hits[0]]
		print("find_satisfied method found no hits.")
		closest_non_hit = None
		inside_hits = []
		outside_hits = []
		for i in range(len(self.all_blocks)):
			inside_blocks = np.array(self.all_blocks[i][0])
			constraint = np.array(self.all_constraints[i])
			# aligned_blocks still have coords relative to the template
			aligned_blocks = inside_blocks[np.nonzero(np.all(inside_blocks - chunk_as_block_center
															 - np.round(inside_blocks - chunk_as_block_center) == 0,
															 axis=1))[0]]
			if len(list(aligned_blocks)) == 0:
				continue
			# block_offsets measures from template origin to the canonical corner of each block
			# (since the aligned blocks are all... aligned, we are basically subtracting the rescaled chosen_center
			# value, which is the fractional part of these blocks' coordinates. But we could've equivalently just
			# rounded down.)
			block_offsets = aligned_blocks - (chunk_as_block_center - chunk_as_block_origin)
			# We find proposed placement of the template by subtracting these.
			proposed_origins = -block_offsets
			# proposed_origins are relative to where the seed's been *translated*, ie,
			# chunk_as_block_origin. We then translate the seed the extra inch...
			# translated_seeds = (chunk_axes_inv_seed - proposed_origins).dot(self.normallel.T)
			# TODO Maybe chunk_axes_inv_seed.dot(self.normallel.T) could be calculated more directly.
			translated_seeds = chunk_axes_inv_seed.dot(self.normallel.T) - proposed_origins.dot(self.normallel.T)
			test_seeds = chunk_axes_inv_seed.dot(self.squarallel) - proposed_origins.dot(self.squarallel)
			# Note, these tests used to be strict, but I added an epsilon
			a_hit = np.all([np.all(self.twoface_normals.dot(translated_seeds.T).T - constraint[:, 0] >= -1e-14, axis=1),
							np.all(self.twoface_normals.dot(translated_seeds.T).T - constraint[:, 1] <= 1e-14, axis=1)],
						   axis=0)
			test_hits = []
			for seed_i in range(len(test_seeds)):
				try:
					fs = self.find_satisfied(test_seeds[seed_i])
					for hit in fs:
						if np.any(np.all(np.array(self.all_blocks[hit][0]) - aligned_blocks[seed_i] == 0, axis=1)):
							if hit == i:
								test_hits.append(hit)
				except Exception:
					pass
			if len(test_hits) > 0:
				print(str(i)+": "+str(test_hits))
			if np.any(a_hit):
				print("We're inside template #" + str(i) + ", at offset" + str(
					block_offsets[np.array(np.nonzero(a_hit))[0, 0]]))
				inside_hits = [(i, proposed_origins[j] + chunk_as_block_origin,
								chunk_axes_inv_seed - proposed_origins[j].dot(self.squarallel)) for j in np.nonzero(a_hit)[0]]
				break
		# Checking outside blocks takes a lot longer, we only want to  do it if we need to
		# At this point, outside hits are a failure condition and virtually always produce errors later on.
		if len(inside_hits) == 0:
			print("No inside hits; checking outside")
			for i in range(len(self.all_blocks)):
				outside_blocks = np.array(self.all_blocks[i][1])
				constraint = np.array(self.all_constraints[i])
				aligned_blocks = outside_blocks[np.nonzero(np.all(outside_blocks - chunk_as_block_center
																  - np.round(
					outside_blocks - chunk_as_block_center) == 0, axis=1))[0]]
				if len(list(aligned_blocks)) == 0:
					# print("Somehow no aligned blocks on template#"+str(i))
					continue
				block_offsets = aligned_blocks - chunk_as_block_center + chunk_as_block_origin
				proposed_origins = -block_offsets
				translated_seeds = (chunk_axes_inv_seed - proposed_origins).dot(self.normallel.T)
				a_hit = np.all([np.all(self.twoface_normals.dot(translated_seeds.T).T >= constraint[:, 0], axis=1),
								np.all(self.twoface_normals.dot(translated_seeds.T).T <= constraint[:, 1], axis=1)],
							   axis=0)
				if np.any(a_hit):
					print("Some sort of neighbor block hit! ")
					# Really, there can only be one hit here because we're looking at one template index i.

					test_vector = np.array([1,2,3,0,0,0]).dot(self.worldplane.T)
					epsilon = 2e-15
					center = aligned_blocks[np.nonzero(a_hit)[0][0]]
					level = 1
					axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[i]][level]
					center_in_world = center.dot(self.worldplane.T)
					target_coords_in_chunk_axes = np.array(center_in_world).dot(axes_matrix) - 0.5
					dist_from_center = np.abs(target_coords_in_chunk_axes)
					test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
					# Which chunk axis is this face on?
					face_indices = np.nonzero(
						np.all(np.array([dist_from_center >= 0.5 - epsilon, dist_from_center <= 0.5 + epsilon]),
							   axis=0))[0]
					face_tests = []
					for face_i in face_indices:
						# Which direction is the face?
						face_sign = np.sign(target_coords_in_chunk_axes[face_i])
						if test_vector_in_chunk_axes[face_i] * face_sign > 0:
							# Test vector points out of this face, so, out of chunk.
							face_tests.append(False)
						else:
							face_tests.append(True)
					print("Template: "+str(i))
					print(target_coords_in_chunk_axes)
					print(test_vector_in_chunk_axes)
					print(face_indices)
					print(face_tests)

					outside_hits += [(i, proposed_origins[j] + chunk_as_block_origin, chunk_axes_inv_seed) for j in np.nonzero(a_hit)[0]]
					#break
		hits = inside_hits + outside_hits
		print("Found " + str(len(hits)) + " possible superchunks.")
		if len(hits) == 0:
			print("(WARNING) Using closest non-hit, which misses the constraint by:")
			print(closest_non_hit[2])
			hits = [(closest_non_hit[0], closest_non_hit[1])]

		return hits

	def generate_children(self, i, offset, level=2, os_children = False):
		"""
		Takes a chunk, represented by a chunk template (as an index i suitable
		for self.all_blocks etc.) together with an offset for where that chunk
		lies, and returns appropriate child chunks, based on the seed, which
		would fill out each 'block' in the given chunk.
		The 'level' of the chunk is the number of times one would have to
		generate children to get to 'block' scale; IE, a level 1 chunk contains
		blocks, a level 2 chunk contains chunks that contain blocks. When given
		a level of 1 or below, however, chunk templates are still returned,
		allowing arbitrary subdivision.
		'offset' is interpreted in the coordinates of the blocks of the chunk -
		ie, at one level below what's given in 'level'.
		Return value is a list of tuples (index,location), giving an index
		suitable for self.all_blocks etc, and a location in coordinates of the
		same level as the children.
		"""

		# Move seed to our offset, then scale it
		#absolute_offset = np.linalg.matrix_power(self.deflation_face_axes, level - 1).dot(offset)
		#translated_seed = (self.get_seed() - absolute_offset).dot(self.squarallel)
		# Seed belongs two levels below the current one
		#current_level_seed = np.linalg.matrix_power(self.deflation_face_axes, 2 - level).dot(translated_seed)
		# Translate seed at our current level
		translated_seed = (self.get_seed(level) - offset)
		# Then represent it at one level below
		current_level_seed = np.array(self.deflation_face_axes,dtype='int64').dot(translated_seed)

		children = []

		chunks = np.array(self.all_blocks[i][0])
		if os_children:
			chunks = np.concatenate([np.array(self.all_blocks[i][0]), np.array(self.all_blocks[i][1])])
		# print("Trying to find "+str(len(chunks))+" children")
		# Take the floor to get the correct origin point of the chunk for lookup.
		points = np.floor(chunks)

		# Taking the floor produces duplicates - an average of 3 copies per
		# point. Removing those would be nice for performance, but removing them
		# right away is inconvenient because when we get several chunks back
		# from the self.find_satisfied call below, we wouldn't know how to try
		# to match them up with the template and discard those not in the "chunks"
		# list. So we create a lookup table so we only have to do the work once.
		unique_points = [points[0]]
		unique_lookup = np.zeros(points[:, 0].shape, dtype=int)
		for chunk_i in range(len(chunks)):
			identical_points = np.all(np.abs(points - points[chunk_i]) < 0.1, axis=1)
			if not np.any(identical_points[:chunk_i]):
				unique_lookup[identical_points] = len(unique_points)
				unique_points.append(points[chunk_i])
		#		points = np.array(unique_points)

		chunkscaled_positions = np.array(self.deflation_face_axes, dtype=int).dot(np.transpose(unique_points)).T
		chunkscaled_offset = np.array(self.deflation_face_axes, dtype=int).dot(offset)
		# Dot product and then subtract *might* reduce overall floating point error.
		chunk_seeds = current_level_seed.dot(self.squarallel) - chunkscaled_positions.dot(self.squarallel)

		# TODO Occasionally the below line leads to an error, with no valid chunks in one of the find_satisfied calls. Why?
		#  May be this only happens when generating children of fairly high-level chunk (say, 13 or so). There's floating
		#  point error right now plaguing those chunks' offset values.
		found_satisfied = [self.find_satisfied(seed) for seed in chunk_seeds]
		# TODO Nested for loops; optimize?
		# for seed_i in range(len(chunk_seeds)):
		for chunk_i in range(len(chunks)):
			# Index into the computations
			u_i = unique_lookup[chunk_i]
			# children.append((self.find_satisfied(chunk_seeds[seed_i]),chunkscaled_positions[seed_i]+chunkscaled_offset))

			location = chunkscaled_positions[u_i] + chunkscaled_offset
			for template_index in found_satisfied[u_i]:
				template_center = self.chunk_center_lookup(template_index)
				# What is the below line doing? We're accepting templates when any axis where template_center has a
				# fractional part, the child's center is integer; and any axis where the child center has a fractional
				# part, the template center is integer. Would've expected a check that they're the same. Maybe this
				# works because the coordinates are expressed on adjacent, but nonequal, levels.
				if np.all((template_center + chunks[chunk_i]) - np.round(template_center + chunks[chunk_i]) != 0):
					children.append((template_index, location))
		return children

	def find_satisfied(self, seedvalue):
		"""
		Takes a seedvalue and returns a list of chunk template indices which
		would satisfy that seed at the origin.
		"""
		seed_15 = self.twoface_normals.dot(seedvalue.dot(self.normallel.T))

		# TODO When I add some sort of testing system, there should be a test
		#  here for whether the single-hit cases still pass the self.satisfies test.
		# The tree ought to get us 1 to 3 possibilities to sort through.
		hits = self.constraint_tree.find(seed_15)
		# Hits can be spurious if the seed doesn't happen to be separated
		# from the constraint region by any of the planes which the tree
		# made use of. (If the seed is outside of a constraint, there's
		# always some plane the tree *could have* tested in order to see this.
		# But when several constraint regions are separated by no single plane,
		# the tree won't test every plane.)
		# TODO If I ever wanted to remove this call to self.satisfies, I could
		#  have the leaf nodes of the tree do some final tests. In principle
		#  the leaf nodes could know which planes haven't been tested yet and
		#  cross their regions, and then use those to determine which
		#  single template to return. Almost equivalent, but easier on the
		#  lookup tree code, would be cutting up all the constraint regions
		#  so that the overlapping regions are their own separate entries on
		#  the constraints list. I'd have a choice of exactly how to cut
		#  everything up yet leave the regions convex.
		if len(hits) == 1:
			# If there's just one, the point must be inside it for two reasons.
			# One, all the bounding constraints got checked. Two, any seed
			# must be in at least one region.
			# Update: Nope, this doesn't seem to be true. When generating parents, most of the translated seeds
			# generated don't have any valid hits (and in fact, out of hundreds of seeds, only one should have a hit).
			# Many of those seeds turn out to generate single false hits, which shouldn't get returned.
			# return hits.
			# TODO It seems like I don't understand this phenomenon well. Which sorts of seeds are so invalid that they
			#  generate no hits? Maybe this corresponds to 6D grid points too far from the worldplane to be a chunk. In
			#  that case, what is it about the generate_parents seed translation process that guarantees only one will
			#  be close enough? Besides the underlying fact that there's only one valid parent, that is.
			pass
		real_hits = []
		for hit in hits:
			if self.satisfies(seedvalue, self.all_constraints[hit]):
				real_hits.append(hit)
		if len(real_hits) > 0:
			return real_hits
		# TODO Some seeds go straight to level 12 or 13 and then get this error.
		#  [ 0.07624056, -0.01408044, -0.00504726, -0.10111274, -0.09552993, -0.04529129]
		#  It appears this is legitimate bad luck... at level after level of superchunk, the origin (and thus player)
		#  ended up too near the edge. Maybe just move player at some point?
		raise Exception("No valid hits out of " + str(len(hits)) + " hits."
						+ "\n Distances from validity:\n"
						+ str([self.satisfies_by(seedvalue, self.all_constraints[i]) for i in hits]))

	def update_player_pos(self, pos, transform):
		trans_inv = transform.basis.inverse()
		rotation = np.array([[transform.basis.x.x, transform.basis.x.y, transform.basis.x.z],
							 [transform.basis.y.x, transform.basis.y.y, transform.basis.y.z],
							 [transform.basis.z.x, transform.basis.z.y, transform.basis.z.z]])
		rotation_inv = np.array([[trans_inv.x.x, trans_inv.x.y, trans_inv.x.z],
								 [trans_inv.y.x, trans_inv.y.y, trans_inv.y.z],
								 [trans_inv.z.x, trans_inv.z.y, trans_inv.z.z]])
		position = np.array([pos.x, pos.y, pos.z])
		translation = np.array([transform.origin.x, transform.origin.y, transform.origin.z])
		self.player_pos = position# - np.array([2.5, 51, -66.7])  # - translation

	def point_at_block(self, mesh_instance, interact_ray, block_place):
		"""
		Starting with collision information (in interact_ray) and the chunk that generated the collision (delivered
		as the mesh_instance created by that chunk), find a targeted block and draw an indicator around it.
		:param mesh_instance:
		:param interact_ray:
		:return:
		"""

		pointed_chunk = ctypes.cast(int(str(mesh_instance.get_meta("originating_chunk"))), ctypes.py_object).value
		collision_point = interact_ray.get_collision_point()
		collision_point = np.array([collision_point.x, collision_point.y, collision_point.z])
		collision_normal = interact_ray.get_collision_normal()
		collision_normal = np.array([collision_normal.x, collision_normal.y, collision_normal.z])

		pointed_at = None
		if pointed_chunk.level == 1:
			blocks = pointed_chunk.get_children()
			block_dists = [block.rhomb_contains_point(collision_point) for block in blocks]
			ranking = block_dists.copy()
			ranking.sort()
			# Theoretically the distance should be 0 for blocks sharing the face that's actually pointed at.
			first_place = ranking[-1]
			second_place = ranking[-2]
			pointed_at = blocks[block_dists.index(first_place)]
			# We don't know whether the chunk contains the 2nd block or not.
			if second_place > -0.1:
				pointed_at_2 = blocks[block_dists.index(second_place)]
				# "pointed_at" is the block *away* from the normal; and then we'll highlight the block that's *toward* it.
				if (pointed_at_2.get_center_position() - collision_point).dot(collision_normal) < 1:
					pointed_at = pointed_at_2
		if pointed_chunk.level == 0:
			pointed_at = pointed_chunk

		#TODO This is the main source of slowness right now. What needs to happen is:
		# - Refactor the core of get_diag_neighbors into a function which takes a list of block offsets, or maybe a list
		#   of hypothetical chunks, and finds the real chunks they correspond to. Such a function can be called in both
		#   get_neighbors and get_diag_neighbors (until I find a better way to do those things). But more to the point,
		#   what we can do here with point_at_block is use the 3D shape of Chunk.neighbors, and try to figure out which
		#   neighbor we actually need. If the neighbor is None, we can deduce its center from the list in
		#   Chunk.neighbor_centers. Then, we can call essentially the get_diag_neighbors algorithm, but on just one
		#   offset, which will be perhaps 20 to 30 times faster.
		# - Avoid calling this every frame. Find a quick way to determine if we're pointing at the same face. (low priority)
		neighbors = [chunk for chunk in pointed_at.get_neighbors(generate=True).flatten() if chunk is not None]
		target = neighbors[0]
		for chunk in neighbors:
			if chunk.rhomb_contains_point(collision_point) > -0.1:
				target = chunk

		if target is not None:
			target.highlight_block()
			self.block_highlight.begin(Mesh.PRIMITIVE_LINES)
			self.block_highlight.set_color(Color(0, 0, 0))
			self.block_highlight.add_vertex(Vector3(collision_point[0], collision_point[1], collision_point[2]))
			second_point = collision_point + collision_normal
			self.block_highlight.add_vertex(Vector3(second_point[0], second_point[1], second_point[2]))
			self.block_highlight.end()

			if block_place:
				target.fill()



	def chunk_at_location(self, target, target_level=0, generate=False, verbose=False):
		"""
		Takes a 3D coordinate and returns the smallest list of already-generated chunks guaranteed to contain that coordinate.
		The search proceeds from the top-level chunk down; if you want to include a guess, call the Chunk.chunk_at_location
		function on your best-guess chunk.
		:param target:
		The coordinates to search for.
		:param target_level:
		The level of chunk desired, with blocks being target_level 0. If chunks of the desired level have not yet been
		generated, by default this will return the closest available level.
		:param generate:
		Set generate=True to force generation of the desired level of chunks. Note, this can either force generation
		down to target_level, or up to target_level, or some combination; for example we can request a chunk of level 10
		(about the scale of Earth's moon), and place it a cauple hundred million blocks away from us (about the distance
		to the moon), and this forces the generation of a highest-level chunk of approximately level 14, subdivided just
		enough to produce the requested level 10 chunk.
		:return: A list of chunks. If target_level < 0, these will be placeholder chunks which represent blocks or sub-blocks.
		"""
		if self.player_guess is None:
			return self.highest_chunk.chunk_at_location(target, target_level, generate, verbose)
		else:
			return self.player_guess.chunk_at_location(target, target_level, generate, verbose)

	def _process(self, delta):
		# Manage a sphere (or maybe spheroid) of loaded blocks around the player.
		# Want to load in just one or a few per update, unload distant ones as the player
		# moves, stop expanding loaded sphere before its size causes frame or memory issues,
		# and on top of all that load really distant super-super-chunks to provide low-LOD distant rendering.
		# To load chunks based on distance, each chunk in a bigger sphere (of superchunks) must already
		# know its center point. To keep the bigger sphere available, each superchunk in a yet-bigger sphere
		# (of super-super-chunks) must know its center-point.
		# Say for sake of argument we have a tiny sphere of blocks, fitting inside one chunk. The sphere of chunks
		# just needs to be big enough that each chunk inside the sphere of blocks (IE, with blocks filled in) has all
		# its neighbors exist (IE, without blocks filled in). So when the sphere of blocks falls exactly within one
		# chunk, there could be just one chunk with loaded blocks, and all its neighbors loaded without their blocks.
		# Next, to maintain this state as we move, we need any superchunk with loaded chunks to also have all
		# neighboring superchunks loaded.
		# Clearly if we proceed like this upwards, we load an infinite number of higher-level chunks. At some point
		# we're loading way more than we need. A really high-level chunk doesn't need to load any neighbors if the
		# player is deep within, thousands of blocks from any face of the chunk.
		# Actually I think it's all very simple. There is a sphere around the player, and we need to generate all
		# blocks within that sphere. This means we need to generate all chunks which might contain blocks within the
		# sphere - which we can simplify to, all chunks with any overlap with the sphere. And to ensure we do that, we
		# generate all superchunks with any overlap with the sphere. We proceed upwards like this until the sphere
		# is strictly contained in some higher-level chunk.
		# There are three problems with that which need addressed.
		# One, what if this never terminates? Couldn't we be on a chunk corner which is also a superchunk corner which
		# is also a super-super-chunk corner, and so on ad infinitum? In the cube case I avoided this issue by
		# selecting an origin for the player to start out at, where they're in the middle of a chunk which is in the
		# middle of a superchunk which is in the middle of a super-super-chunk, and so on and so on ad infinitum. This
		# way, the player is infinitely far from any points with that problem. But on the aperiodic grid, I'm actually
		# starting the player off at a random point, so how can I be sure? Well, every higher level of chunk corners
		# actually represents 6D lattice points which are an order of magnitude closer to the world-plane. So a point
		# could be extremely close and remain an intersection for quite a while, but eventually there will be some
		# level of chunk where it's excluded. This means that chunk corners are guaranteed get further and further away
		# if we go up enough levels. Since the seed is chosen to be non-singular, no 6D point lies exactly on the world.
		# Second, blocks cross chunk boundaries! So the loading sphere could be entirely contained within some
		# super-chunk, yet it might intersect a chunk which belongs to some neighbor super-chunk. This could be addressed
		# directly by using the actual ownership boundary of each chunk (but just based on direct sub-chunks) instead
		# of the rhombohedral boundary. An alternative would be to determine some distance from the boundary and
		# simply assume that points closer than that might be intersecting a neighbor. This effectively means the sphere
		# gets bigger at each stage, yet my instinct is that it would be OK. Finally, the way I've calculated chunk
		# templates, each one actually knows positions of any neighboring blocks which reach inside the template. So
		# a chunk can just check whether neighboring sub-chunks intersect the sphere, and then load in the corresponding
		# neighboring chunk.
		# Third, checking for actual overlap with a sphere may be expensive, even if we're just doing it with
		# rhombohedra rather than a sub-chunk outline. One solution might be to, again, increase the size of the sphere
		# at each stage, just enough so that we can switch to a check for intersecting corners rather than arbitrary
		# intersection. So at each level we'd start with the original sphere, then consider the worst-case placement of
		# that sphere tangent to a golden rhombus of the current chunk scale, and increase the radius just enough that
		# it would contain the rhombus' corners in such a case. Would the process ever stop making superchunks? I think
		# it would, but it would produce many more levels of superchunk than necessary. Better to just write a nice
		# sphere intersection test.
		# Finally, we shouldn't just expand such a sphere until we flirt with memory and rendering limits. The
		# dropoff in detail after the sphere is exited is too harsh. Ideally what we want is for parts of the world
		# which the player can actually see to become more detailed, without too much switching back and forth as to
		# what is and isn't loaded, and with fairly even coverage.
		# ... This is me many months later, re-reading the above. We could choose some big-enough chunks, call it the
		# "level on watch". On the level on watch, keep the chunk loaded where the player is found, along with all its
		# diagonal neighbors. The level below this is the "load/unload level". All loaded "level on watch" chunks'
		# children are part of the "load/unload level", and are being constantly compared with the player's position,
		# so that high-priority chunks (where the player is looking or walking towards for example) can be loaded. When
		# things are going exceptionally well resources-wise, the level on watch can be raised by one; or when things
		# are bogged down, it could even be lowered. But that's a very coarse adjustment to the scale of what's being
		# loaded and unloaded.
		if r.random() < 0.95:
			return
		# For now, we use a loading radius, which cautiously expands.
		# #np.concatenate([self.all_blocks[t_i][1],
		#                       #[self.all_blocks[t_i][0][block_i] for block_i in range(len(self.all_blocks[t_i][0]))
		#                       # if block_i in to_skip]])
		#                                         )
		#TODO We can make this location search much faster whenever the player is colliding with terrain, by having
		# that terrain form the starting point of the search. Or really, since we just need a close enough location
		# for chunk loading purposes, the terrain collision would give us everything we need.
		if self.player_guess is None or len(self.player_guess) == 0:
			self.player_guess = [self.highest_chunk]
		random.shuffle(self.player_guess)
		investigation = self.player_guess.pop().increment_search(self.player_pos)
		for lead in investigation:
			self.player_guess.append(lead)
		print(self.player_guess)
		if len(self.player_guess) == 0:
			print("Huh, had to reset")
			self.player_guess = [self.highest_chunk]
		# TODO Perhaps we want to choose the best match rather than the first-encountered. Also, if one branch of
		#  the search turns out fruitless and backs off, that could trigger the other branches to be abandoned.
		lowest_guess_level = min([guess.level for guess in self.player_guess])
		for guess in self.player_guess:
			if guess.safely_contains_point(self.player_pos) and guess.level == lowest_guess_level:
				self.player_guess = [guess]
		uniques = []
		for guess in self.player_guess:
			if guess not in uniques:
				uniques.append(guess)
		self.player_guess = uniques
		return
		self.block_highlight.clear()
		# self.block_highlight.set_color(Color(.1,.1,.1))
		# Is the player contained in a fully generated chunk?
		closest_chunks = []
		try:
			closest_chunks = self.chunk_at_location(self.player_pos)
		except Exception as e:
			print("Exception during non-generative search for player")
			guess = e.args[1]
			print("I'm assuming the player is in a hole in the terrain.")
			print("Preparing debug info...")
			os_children_templates = self.generate_children(guess.template_index, guess.offset,
														   guess.level, os_children=True)
			os_children_chunks = [
				Chunk(self, os_children_templates[i][0], os_children_templates[i][1], guess.level - 1)
				for i in range(len(os_children_templates))]
			os_children_centers = (self.all_blocks[guess.template_index][0]
								   + self.all_blocks[guess.template_index][1])
			containing_children = []
			for i in range(len(os_children_templates)):
				child = os_children_chunks[i]
				if child.rhomb_contains_point(self.player_pos) >= 0:
					containing_children.append(i)
			print("Found " + str(len(containing_children)) + " outsider children containing player.")
			for child_i in containing_children:
				print("Child at level " + str(os_children_chunks[child_i].level))
				if child_i < len(self.all_blocks[guess.template_index][0]):
					print("This one is inside the chunk; should've been found via generating children.")
				test_vector = np.array([1, 2, 3, 0, 0, 0]).dot(self.worldplane.T)
				epsilon = 2e-15
				center = os_children_centers[child_i]
				level = 1
				axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[guess.template_index]][level]
				center_in_world = center.dot(self.worldplane.T)
				target_coords_in_chunk_axes = np.array(center_in_world).dot(axes_matrix) - 0.5
				dist_from_center = np.abs(target_coords_in_chunk_axes)
				test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
				# Which chunk axis is this face on?
				face_indices = np.nonzero(
					np.all(np.array([dist_from_center >= 0.5 - epsilon, dist_from_center <= 0.5 + epsilon]),
						   axis=0))[0]
				face_tests = []
				for face_i in face_indices:
					# Which direction is the face?
					face_sign = np.sign(target_coords_in_chunk_axes[face_i])
					if test_vector_in_chunk_axes[face_i] * face_sign > 0:
						# Test vector points out of this face, so, out of chunk.
						face_tests.append(False)
					else:
						face_tests.append(True)
				print("Template: " + str(guess.template_index))
				print("Block center in chunk axes:")
				print(target_coords_in_chunk_axes)
				print("Test vector in chunk axes:")
				print(test_vector_in_chunk_axes)
				print(face_indices)
				print(face_tests)
		if len(closest_chunks) != 1 or closest_chunks[0].level != 0:
			print(str(len(closest_chunks)) + " results from search for player. Level: " + str(
				min([c.level for c in closest_chunks] + [1000])))
		for closest_chunk in closest_chunks:
			self.player_guess = closest_chunk
			# closest_chunk.highlight_block()
			# closest_chunk.get_parent().highlight_block()
			# closest_chunk.get_parent().get_parent().highlight_block()
			# self.block_highlight.show()
			if not closest_chunk.drawn:
				closest_chunk.draw_mesh()
			if closest_chunk.level > 1 or (closest_chunk.level == 1 and not closest_chunk.all_children_generated):
				# If not, generating that chunk is enough for this frame; do it and return.
				# But first, reduce the loading_radius since it obviously failed.
				print("Search found chunk of level " + str(closest_chunk.level) + ". Children generated? " + str(
					closest_chunk.all_children_generated))
				# TODO It would be nice for testing to be able to discover whether anything new generates when generate=True.
				# print("You need some ground to stand on! Trying to draw it in")
				new_ground = []
				try:
					new_ground = closest_chunk.chunk_at_location(self.player_pos, target_level=0, generate=True)
				except:
					print("I'm assuming the player is in a hole in the terrain.")
					print("Preparing debug info...")
					os_children_templates = self.generate_children(closest_chunk.template_index, closest_chunk.offset,
														 closest_chunk.level,os_children = True)
					os_children_chunks = [Chunk(self, os_children_templates[i][0], os_children_templates[i][1], closest_chunk.level - 1)
										  for i in range(len(os_children_templates))]
					os_children_centers = (self.all_blocks[closest_chunk.template_index][0]
										   + self.all_blocks[closest_chunk.template_index][1])
					containing_children = []
					for i in range(len(os_children_templates)):
						child = os_children_chunks[i]
						if child.rhomb_contains_point(self.player_pos) >= 0:
							containing_children.append(i)
					print("Found "+str(len(containing_children))+" outsider children containing player.")
					for child_i in containing_children:
						print("Child at level "+str(os_children_chunks[child_i].level))
						if child_i < len(self.all_blocks[closest_chunk.template_index][0]):
							print("This one is inside the chunk; should've been found via generating children.")
						test_vector = np.array([1,2,3,0,0,0]).dot(self.worldplane.T)
						epsilon = 2e-15
						center = os_children_centers[child_i]
						level = 1
						axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[closest_chunk.template_index]][level]
						center_in_world = center.dot(self.worldplane.T)
						target_coords_in_chunk_axes = np.array(center_in_world).dot(axes_matrix) - 0.5
						dist_from_center = np.abs(target_coords_in_chunk_axes)
						test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
						# Which chunk axis is this face on?
						face_indices = np.nonzero(
							np.all(np.array([dist_from_center >= 0.5 - epsilon, dist_from_center <= 0.5 + epsilon]),
								   axis=0))[0]
						face_tests = []
						for face_i in face_indices:
							# Which direction is the face?
							face_sign = np.sign(target_coords_in_chunk_axes[face_i])
							if test_vector_in_chunk_axes[face_i] * face_sign > 0:
								# Test vector points out of this face, so, out of chunk.
								face_tests.append(False)
							else:
								face_tests.append(True)
						print("Template: " + str(closest_chunk.template_index))
						print("Block center in chunk axes:")
						print(target_coords_in_chunk_axes)
						print("Test vector in chunk axes:")
						print(test_vector_in_chunk_axes)
						print(face_indices)
						print(face_tests)


				if closest_chunk in new_ground:
					print("Got same chunk back. Children generated? " + str(closest_chunk.all_children_generated))
					print("Did the search go exactly the same way? " + str(new_ground == closest_chunks))
				return
		if len(closest_chunks) == 0:
			print("\n\tBroader chunk tree needed! Generating...\t")
			try:
				closest_chunks = self.chunk_at_location(self.player_pos, target_level=0, generate=True, verbose=True)
			except Exception as e:
				print("Exception during attempt to broaden.")
				guess = e.args[1]
				print("I'm assuming the player is in a hole in the terrain.")
				print("Preparing debug info...")
				os_children_templates = self.generate_children(guess.template_index, guess.offset,
															   guess.level, os_children=True)
				os_children_chunks = [
					Chunk(self, os_children_templates[i][0], os_children_templates[i][1], guess.level - 1)
					for i in range(len(os_children_templates))]
				os_children_centers = (self.all_blocks[guess.template_index][0]
									   + self.all_blocks[guess.template_index][1])
				containing_children = []
				for i in range(len(os_children_templates)):
					child = os_children_chunks[i]
					if child.rhomb_contains_point(self.player_pos) >= 0:
						containing_children.append(i)
				print("Found " + str(len(containing_children)) + " outsider children containing player.")
				for child_i in containing_children:
					print("Child at level " + str(os_children_chunks[child_i].level))
					if child_i < len(self.all_blocks[guess.template_index][0]):
						print("This one is inside the chunk; should've been found via generating children.")
					test_vector = np.array([1, 2, 3, 0, 0, 0]).dot(self.worldplane.T)
					epsilon = 2e-15
					center = os_children_centers[child_i]
					level = 1
					axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[guess.template_index]][level]
					center_in_world = center.dot(self.worldplane.T)
					target_coords_in_chunk_axes = np.array(center_in_world).dot(axes_matrix) - 0.5
					dist_from_center = np.abs(target_coords_in_chunk_axes)
					test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
					# Which chunk axis is this face on?
					face_indices = np.nonzero(
						np.all(np.array([dist_from_center >= 0.5 - epsilon, dist_from_center <= 0.5 + epsilon]),
							   axis=0))[0]
					face_tests = []
					for face_i in face_indices:
						# Which direction is the face?
						face_sign = np.sign(target_coords_in_chunk_axes[face_i])
						if test_vector_in_chunk_axes[face_i] * face_sign > 0:
							# Test vector points out of this face, so, out of chunk.
							face_tests.append(False)
						else:
							face_tests.append(True)
					print("Template: " + str(guess.template_index))
					print("Block center in chunk axes:")
					print(target_coords_in_chunk_axes)
					print("Test vector in chunk axes:")
					print(test_vector_in_chunk_axes)
					print(face_indices)
					print(face_tests)
			print("\n\tBroadening resulted in " + str(len(closest_chunks)) + " search results.\n")
			return


		load_radius = 10
		# Starting at the last known player location:
		containing_chunk = self.player_guess
		#	# Does this chunk fully contain the sphere? That is, does the sphere fall within 'safe' inner margins,
		#	# where neighbor chunks won't intrude?
		#	#	# If yes, do procedure 'alpha':
		#	#	#  Identify all sub-chunks which overlap the sphere.
		#	#	#  Is any of them not subdivided into sub-sub-chunks?
		#	#	#	# If yes, do procedure 'add and prune':
		#	#	#	#	# Are we at the limit of number of loaded chunks?
		#	#	#	#	#	# If yes, identify a low-priority chunk to unload.
		#	#	#	#	# Generate children for the identified chunk.
		#	#	#	# If no, repeat procedure alpha on each sub-chunk.
		#	#	# If no: do any neighbor sub-chunks (from the outer part of our template) overlap the sphere?
		#	#	#	# If yes, add a new top-level chunk, and re-start the process there.
		#	#	#	# If no, we do fully contain it. Do procedure 'alhpa' above.
		pass

	def _ready(self):
		starttime = time.perf_counter()

		# This variable is temporary until I use actual round planets
		self.gravity_direction = Vector3(0, -1, 0)

		# self.convert_chunklayouts()

		print("Loading from existing file...")

		self.all_constraints = []
		self.all_blocks = []
		self.blocklist = []

		print(time.perf_counter() - starttime)
		print("Loading...")

		self.inside_blocks_bools = np.array([])
		self.outside_blocks_bools = np.array([])
		self.load_templates_npy("templates_test_vector_123")
		print("Done loading " + str(len(self.all_constraints)) + " templates")
		print(time.perf_counter() - starttime)

		# Lookup table for Chunk.rhomb_contains_point
		# Uses possible_centers since there are as many of them as there are axis setups.
		# As the level goes up, these are merely rescaled.
		self.axes_matrix_lookup = {center: [np.linalg.inv(
			self.worldplane.T[np.nonzero(
				self.possible_centers_live[self.possible_centers.index(center)]
				- np.floor(self.possible_centers_live[self.possible_centers.index(center)]) - 0.5)[0]]
			* self.phipow(3 * level)) for level in range(10)] for center in self.possible_centers}

		print("Created axes matrix lookup table")
		print(time.perf_counter() - starttime)

		self.constraint_nums = [set(), set(), set(), set(), set(), set(), set(), set(), set(), set(),
								set(), set(), set(), set(), set()]
		for i in range(len(self.all_constraints)):
			for j in range(15):
				self.constraint_nums[j] = self.constraint_nums[j].union(set(self.all_constraints[i][j]))
		for i in range(15):
			sorted = list(self.constraint_nums[i])
			sorted.sort()
			self.constraint_nums[i] = sorted

		# Original, pre-simplification size of constraint_nums in each dimension:
		# 400, 364, 574, 372, 395, 359, 504, 553, 382, 369, 470, 556, 404, 351, 359
		# After 20 calls of self.simplify_constraints():
		# 359, 315, 514, 336, 343, 325, 440, 509, 339, 338, 411, 500, 377, 328, 324

		do_check_overlap = False
		if do_check_overlap:
			print("Removing duplicate blocks...")

			# Checking for overlap with neighbors!
			# This is doubtless slow, but I have to do it for now.
			# OK, after the below testing, here are the facts:
			# - Sadly, block centers do sometimes fall exactly on chunk boundaries. This is something I'd been hoping
			#   was not true since it makes block ownership very ambiguous.
			# - I tried testing the block's origin to "break the tie", and found that it, too, was sometimes on the
			#   boundary, so no decision could be made.
			# - Additionally, it should be noted that sometimes the origin is the same distance out from each chunk,
			#   but that distance is about 0.236. Surely, this means the origin would fall in some other neighbor; but
			#   I haven't verified that.
			# - I tried introducing a 'test point', specifically (1, 0, 0) in the block's three axes, but this too
			#   turned out to fall on the boundary some of the time, so didn't break all ties.
			# - Introducing a second test point, (0, 1, 0), appears to break all ties.
			# Note: Above procedure doesn't work. A block can overlap three or more chunks. The first test point (center)
			#  can fall outside some chunk (X) but on the boundary of another (Y). Then, the second test point (origin) can
			#  fall within the first chunk (X). Both chunks will then deny ownership of the block.
			# So, time for a new scheme.

			# We'll use the center of each block, and a test vector. If a block center is on a chunk boundary, the test
			# vector points towards the chunk which will take ownership. We just need a test vector which is not
			# parallel to any of the edges or faces in the lattice.

			# First idea: we want to point along the long axis of a prolate rhombohedron. Won't work: this is paralles
			#  to the face of (I believe) a prolate rhombohedron which shares 1 of the edge directions.
			# OK: possible faces of blocks/chunks correspond to edges of an icosahedron (well, their cone thru
			# the center). My first idea picked the center of an icosahedron face. But these edge lines need to be
			# extended across the icosahedron faces, splitting each triangle in six. So: select the center of one
			# of these 120 faces. We can get this with the previous face-center ([1,1,1,0,0,0]) plus an edge center
			# ([0,1,1,0,0,0]) plus a corner ([0,0,1,0,0,0]).

			test_vector = np.array([1,2,3,0,0,0]).dot(self.worldplane.T)

			# It seems (tho, after very few tests) that an epsilon value of 2e-15 is too high, and still produces
			# overlap bettween chunks. An epsilon value of 1e-15 is too low, and still produces holes.
			epsilon = 2e-15
			# The block centers themselves are purely half-integer 6D values, so either the projection to 3D or the
			# conversion into the chunk axes is introducing enough error that, apparently, on-boundary and off-boundary
			# cannot be strictly differentiated with an epsilon test.
			# Update: found no values occurring between 1e-15 and 0.001. So the epsilon test is fine, and the problem
			# lies elsewhere. The fact that I'm getting both holes and overlap suggests the algorithm is basically
			# flawed or I've made some typo in implementing it.

			def rhomb_contains_point(point, template_index, self=self):
				level = 1
				axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[template_index]][level]
				target_coords_in_chunk_axes = np.array(point).dot(axes_matrix) - 0.5
				# To measure distance from closest face-plane, we take the minimum of the absolute value.
				dist_from_center = np.abs(target_coords_in_chunk_axes)
				return np.min(0.5 - dist_from_center)


			def intersection_type(point, template_index, self=self):
				"""
				Returns -1 if the point is outside the chunk; 0 if it is in the interion; 1 if it is on a face;
				2 if it is on an edge; and 3 if it is on a vertex.
				:param point: The point to test
				:param template_index: The template index of the chunk
				:param self: The chunk network providing template data
				:return: An integer, between -1 and 3 inclusive.
				"""
				level = 1
				axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[template_index]][level]
				target_coords_in_chunk_axes = np.array(point).dot(axes_matrix) - 0.5
				dist_from_center = np.abs(target_coords_in_chunk_axes)
				if abs(np.max(dist_from_center)-0.5) > 1e-15:
					if abs(np.max(dist_from_center)-0.5) < 0.001:
						print(np.max(dist_from_center)-0.5)
				if np.max(dist_from_center) > 0.5 + epsilon:
					# It's outside the chunk
					return -1
				if np.max(dist_from_center) < 0.5 - epsilon:
					# It's inside the chunk
					return 0
				# It's on the boundary, so the return value is just the count of on-boundary axes.
				return np.sum(np.abs(dist_from_center - 0.5) <= epsilon)

			for t_i in range(len(self.all_blocks)):
				to_skip = []
				blocks = np.concatenate([self.all_blocks[t_i][0], self.all_blocks[t_i][1]])
				# TODO Should be more certain of no duplicates in "blocks".
				for block_i in range(len(blocks)):
					center = blocks[block_i]
					level = 1
					axes_matrix = self.axes_matrix_lookup[self.all_chosen_centers[t_i]][level]
					center_in_world = center.dot(self.worldplane.T)
					target_coords_in_chunk_axes = np.array(center_in_world).dot(axes_matrix) - 0.5
					dist_from_center = np.abs(target_coords_in_chunk_axes)
					intersection = intersection_type(center.dot(self.worldplane.T), t_i)

					if intersection ==  -1:
						# A block whose center lies outside of us is definitely skipped.
						to_skip.append(block_i)
					elif intersection == 0:
						# A block whose center lies inside is definitely not skipped
						pass
					elif intersection == 1:
						# Intersects on a face. We need to see if our test vector points into the face or out of it.
						test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
						# Which chunk axis is this face on?
						face_index = np.nonzero(np.all(np.array([dist_from_center >= 0.5 - epsilon, dist_from_center <= 0.5 + epsilon]),axis=0))[0][0]
						# Which direction is the face?
						face_sign = np.sign(target_coords_in_chunk_axes[face_index])

						if test_vector_in_chunk_axes[face_index]*face_sign > 0:
							# Test vector points out of face; the other chunk will take responsibility.
							to_skip.append(block_i)
						else:
							# We keep this one.
							pass
					elif intersection == 2:
						print("Encountered a block center on an edge.")
						# Intersection on an edge. We'll claim the block if the test vector points into the edge; IE,
						# into both adjacent faces.
						# NOTE: This apparently does not ever happen. I should satisfy myself that it's mathematically
						# impossible and then remove the case.
						test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
						# Which chunk axis is this face on?
						face_indices = np.nonzero(np.all(np.array([dist_from_center >= 0.5 - epsilon, dist_from_center <= 0.5 + epsilon]),axis=0))[0]
						if len(face_indices) != 2:
							raise Exception("You need to take a closer look at your code.")
						face_tests = []
						for face_i in face_indices:
							# Which direction is the face?
							face_sign = np.sign(target_coords_in_chunk_axes[face_i])
							if test_vector_in_chunk_axes[face_i] * face_sign > 0:
								# Test vector points out of this face, so, out of chunk.
								face_tests.append(False)
							else:
								face_tests.append(True)
						if np.all(face_tests):
							# Test vector points into edge; this one's ours.
							pass
						else:
							# A different chunk along this edge will take this block.
							to_skip.append(block_i)
					elif intersection == 3:
						raise Exception(
							"Test point was on chunk corner. Did you use a block corner as a test point? Or did something else go wrong?")

				print("Removing " + str(len(to_skip)) + " blocks out of " + str(len(self.all_blocks[t_i][0])))
				# We just shift it over to the "outside" list.
				self.all_blocks[t_i] = ([np.concatenate([self.all_blocks[t_i][0], self.all_blocks[t_i][1]])[block_i] for block_i in range(len(np.concatenate([self.all_blocks[t_i][0], self.all_blocks[t_i][1]])))
										 if block_i not in to_skip], [np.concatenate([self.all_blocks[t_i][0], self.all_blocks[t_i][1]])[block_i] for block_i in range(len(np.concatenate([self.all_blocks[t_i][0], self.all_blocks[t_i][1]])))
										 if block_i in to_skip]
										# np.concatenate([self.all_blocks[t_i][1],
										# [self.all_blocks[t_i][0][block_i] for block_i in range(len(self.all_blocks[t_i][0]))
										# if block_i in to_skip]])
										)
			print("Removed dupes in templates.")
			print(time.perf_counter() - starttime)

		# self.blocklist contains *all* blocks. Let's make a similar list for inside blocks.
		is_blocks_bool = np.any(self.inside_blocks_bools,axis=0)
		self.is_blocklist = self.blocklist[np.nonzero(is_blocks_bool)[0]]
		self.is_to_all_bool_lookup = np.nonzero(is_blocks_bool)[0]
		# Some stuff to help speed up generate_parents()
		block_alignments = np.round(2*np.linalg.inv(self.deflation_face_axes).dot(np.array(self.possible_centers_live).T).T)/2
		print(block_alignments)
		is_blocklist_alignment_lookup = np.nonzero(np.all(np.modf(np.repeat([self.is_blocklist],len(block_alignments)
																				 ,axis=0)
															   - np.repeat([block_alignments],len(self.is_blocklist)
																		   ,axis=1)
															   .reshape(len(block_alignments),len(self.is_blocklist),6)
																	   )[0] == 0, axis=2))
		self.is_blocklist_alignment_lookup = [
			[is_blocklist_alignment_lookup[1][i] for i in
			 range(is_blocklist_alignment_lookup[1].shape[0]) if is_blocklist_alignment_lookup[0][i] == alignment]
			for alignment in range(20)]
		# TODO Other things I could precompute (but, not sure how much benefit this could be):
		#  - Chunkscaled block coords.
		#  - Floor of block coords (block origins)
		#  - Differences between floors and the original numbers
		#  - The "unique origins" lookup table produced in generate_children
		#  - Block origins dotted with self.squarallel, which is what gets used when translating seeds
		#  - Basically anything else which gets used anywhere


		# Now that constraints have considerably less points, we probably need considerably less of them.
		# TODO Make re-simplifying and redoing the constraint tree easier.
		#self.test_templates()#(True)
		#print("Going to simplify")
		#self.simplify_constraints()
		#print("Simplified once")
		#self.simplify_constraints()
		#self.simplify_constraints()
		#print("Simplified thrice")
		#self.simplify_constraints()
		#self.simplify_constraints()
		#self.simplify_constraints()
		#print("Going to save")
		#self.save_templates_npy("templates_test_vector_123")


		# Now with somewhat more compact constraints, we can create a decent-speed
		# lookup tree.

		#self.constraint_tree = ConstraintTree.sort(self.all_constraints, list(range(len(self.all_constraints))), self.constraint_nums)
		#self.constraint_tree.save("templates_test_vector_123.tree")
		#print("Tree has been saved!")
		#print("Done constructing constraint tree")
		self.constraint_tree = ConstraintTree.load("templates_test_vector_123.tree")
		print("Done loading constraint search tree.")
		print(time.perf_counter() - starttime)

		# Generating templates for block neighbor relationships within chunks.
		# I want to pre-compute as much about neighbor relationships as I can, seeing as I just heavily optimized
		# my neighbor computations and it still sometimes takes about a second. If I can make this part much faster,
		# I can even use neighbor information for other things, such as the 'creeping' algorithm for locating a block.
		# Types of information to compute:
		# - Which blocks share faces, in is_blocks and beyond.
		# - "Diagonal neighbors", along with whether the list is complete.
		# - When neighbors will be in a different chunk, we can't predict what shape the chunk will be, but we can
		#   predict exactly what offset the neighbor will be at -- which would make the first step in my current
		#   diagonal neighbor search (generating a bunch of children, & defining the whole "diagonal neighbor" concept
		#   according to where the os_children fall) unnecessary.
		#TODO Precomputing offsets of neighbors will remove the last little bit of need for os_children. Might be smart,
		# once this stuff is written, to consider actually merging some functionally identical chunks together to reduce
		# the number of children. By functionally identical, I mean, the same is_children and the same generated
		# neighbor data.

		# First we simply compute potential neighbor information amongst all possible blocks
		repeated_blocklist = np.repeat([self.blocklist], len(self.blocklist), axis=0)
		bl_diffs = np.abs(repeated_blocklist - np.transpose(repeated_blocklist, (1,0,2)))
		bl_diffs_of_half = bl_diffs == 0.5
		bl_diffs_of_one = bl_diffs == 1
		bl_diffs_of_zero = bl_diffs == 0
		# Neighbors sharing faces
		bl_blocks_neighbor = (np.sum(bl_diffs_of_half, axis=2) == 2) * (np.sum(bl_diffs_of_zero, axis=2) == 4)
		# Block centers neighbor diagonally (sharing a corner) if there exists an integer lattice point (corner)
		# which differs from both by 0.5 in three of the six dimensions. Depending on overlap in which dimensions
		# differ from the corner, this can mean six dimensions differing in 0.5, three differing by exactly 1, or
		# many other possibilities; but the sum of the differences will be 3 or less. And, whenever the sum of differences
		# is 3 or less and the differences do not exceed one, there will be at least one corner shared.
		bl_blocks_neighbor_diag = ((np.sum(bl_diffs_of_one, axis=2) + np.sum(bl_diffs_of_half, axis=2)
									+ np.sum(bl_diffs_of_zero, axis=2) == 6) * (np.sum(bl_diffs, axis=2) <= 3)) \
								  * (np.sum(bl_diffs_of_zero, axis=2) < 6)

		# More lookup tables with poor naming conventions
		self.all_blocks_neighbor = []
		self.all_blocks_neighbor_diag = []
		self.all_neighbors_outside_chunk = []
		self.all_diag_neighbors_outside_chunk = []
		for template_i in range(len(self.all_blocks)):
			#print(template_i)
			template = self.all_blocks[template_i]
			# We're counting on each template's blocklist being in the same order in which the blocks fall in self.blocklist
			# Here's what a test would look like
			# print(np.nonzero(self.all_blocks[template_i][0]
			# 				 - self.blocklist[np.nonzero(self.inside_blocks_bools[template_i])[0]]))
			inside_block_indices = np.nonzero(self.inside_blocks_bools[template_i])[0]
			combined_block_indices = np.concatenate([inside_block_indices, np.nonzero(self.outside_blocks_bools[template_i])[0]])
			# We'll do calculations with both inside and outside blocks
			blocks_neighbor = bl_blocks_neighbor[combined_block_indices][:,combined_block_indices]
			blocks_neighbor_diag = bl_blocks_neighbor_diag[combined_block_indices][:,combined_block_indices]
			# We store the inside_block subset
			self.all_blocks_neighbor.append(blocks_neighbor[:len(template[0]), :len(template[0])])
			self.all_blocks_neighbor_diag.append(blocks_neighbor_diag[:len(template[0]), :len(template[0])])

			# Next we want to store specific offsets from outside neighbors.
			# For each block, there will be a list of offsets (well, actually, block centers).
			neighbors_outside_chunk = []
			diag_neighbors_outside_chunk = []
			for block_i in range(len(template[0])):
				face_neighbors = np.nonzero(blocks_neighbor[block_i,len(template[0]):len(template[1])])[0]
				diag_neighbors = np.nonzero(blocks_neighbor_diag[block_i,len(template[0]):len(template[1])])[0]
				neighbors_outside_chunk.append(np.array(template[1])[face_neighbors])
				diag_neighbors_outside_chunk.append(np.array(template[1])[diag_neighbors])
			self.all_neighbors_outside_chunk.append(neighbors_outside_chunk)
			self.all_diag_neighbors_outside_chunk.append(diag_neighbors_outside_chunk)

		print("Done generating neighbor information.")
		print(time.perf_counter() - starttime)


		# Choose one chunk to display
		chunk_num = r.choice(range(len(self.all_blocks)))
		print("Chosen chunk:"+str(chunk_num))
		chosen_center = self.chunk_center_lookup(chunk_num)
		inside_blocks = self.all_blocks[chunk_num][0]
		outside_blocks = self.all_blocks[chunk_num][1]

		print("Chosen center: " + str(chosen_center))

		array_mesh = ArrayMesh()
		self.mesh = array_mesh

		# Now try to find a super-chunk for this chunk

		# First we have to find an offset value within the chunk constraints.
		# I'll call this the "seed" since it will determine the entire lattice.

		# Starting value, will get moved to inside the chosen chunk orientation constraints.
		self.original_seed = np.array([r.random(), r.random(), r.random(), r.random(), r.random(), r.random()])
		self.original_seed = self.original_seed.dot(self.squarallel)

		self.center_guarantee = dict()
		for center in self.possible_centers_live:
			center_axes = 1 - np.array(center - np.floor(center)) * 2
			center_origin = center - np.array(self.deflation_face_axes).T.dot(center_axes) / 2
			center_axis1 = np.array(self.deflation_face_axes[np.nonzero(center_axes)[0][0]])
			center_axis2 = np.array(self.deflation_face_axes[np.nonzero(center_axes)[0][1]])
			center_axis3 = np.array(self.deflation_face_axes[np.nonzero(center_axes)[0][2]])
			chunk_corners = np.array([center_origin,
									  center_origin + center_axis1, center_origin + center_axis2,
									  center_origin + center_axis3,
									  center_origin + center_axis1 + center_axis2,
									  center_origin + center_axis1 + center_axis3,
									  center_origin + center_axis2 + center_axis3,
									  center_origin + center_axis1 + center_axis2 + center_axis3])
			a = np.sum(chunk_corners, axis=0) / 8
			center_constraints = np.sum(
				np.stack(np.repeat([chunk_corners - a], 30, axis=0), axis=1).dot(self.normallel.T)
				* np.concatenate(np.array([self.twoface_normals, -self.twoface_normals]).reshape((1, 30, 3))), axis=2)
			overall_center_constraints = 0.9732489894677302 / (self.phi * self.phi * self.phi) - np.max(
				center_constraints, axis=0)
			translated_constraints = (overall_center_constraints * np.concatenate([-np.ones(15), np.ones(15)])
									  + np.concatenate([self.twoface_normals, self.twoface_normals]).dot(
						a.dot(self.normallel.T)))
			translated_constraints = (translated_constraints).reshape((2, 15)).T
			self.center_guarantee[str(center)] = translated_constraints

		ch3_member = np.ceil(chosen_center) - np.floor(chosen_center)
		three_axes = np.nonzero(ch3_member)[0]
		constraint_dims = np.nonzero(1 - np.any(self.twoface_axes - ch3_member > 0, axis=1))[0]
		# constraint_dims gives us indices into center_guarantee as well as twoface_axes,
		# twoface_normals and twoface_projected.
		for i in constraint_dims:
			third_axis = np.nonzero(ch3_member - self.twoface_axes[i])[0][0]
			axis_scale = np.eye(6)[third_axis].dot(self.normallel.T).dot(self.twoface_normals[i])
			divergence = self.center_guarantee[str(chosen_center)][i] - self.twoface_normals[i].dot(
				self.original_seed.dot(self.normallel.T))
			# Is point outside the constraints in this direction?
			if divergence[0] * divergence[1] >= 0:
				rand_pos = r.random()
				move = (divergence[0] * rand_pos + divergence[1] * (1 - rand_pos)) * np.eye(6)[third_axis].dot(
					self.normallel.T) / axis_scale
				self.original_seed = self.original_seed + move.dot(self.normallel)

				generates_correct_chunk = (np.all(self.twoface_normals.dot(self.original_seed.dot(self.normallel.T))
												  > self.center_guarantee[str(chosen_center)][:, 0])
										   and np.all(self.twoface_normals.dot(self.original_seed.dot(self.normallel.T))
													  < self.center_guarantee[str(chosen_center)][:, 1]))
				if generates_correct_chunk:
					# Break early before we mess it up
					break
		self.make_seed_within_constraints(self.all_constraints[chunk_num])
		print("Chose a seed within constraints for template #" + str(chunk_num) + ":")
		print(self.original_seed)

		# Now that "seed" is a valid offset for our chosen chunk, we need to
		# determine which superchunk it can fit in.
		# There should logically be just one option, since the seed uniquely
		# determines the whole grid.
		# TODO: (Runs so far have always found either 1 or 2 valid superchunks.
		#  But, should do a more rigorous test, ideally verifying back in
		#  numpylattice.py that this is inevitable.)
		#  Addendum: For perhaps months, no run has produced 2 superchunks, and I don't know why. I now believe that
		#  the cause of getting 2 superchunks was actual overlap between chunk templates. I've corrected the overlap
		#  but I don't know why the 2 superchunks thing stopped happening long before I corrected it.

		self.highest_chunk = Chunk(self, chunk_num, [0, 0, 0, 0, 0, 0], 1)
		self.highest_chunk.is_topmost = True
		self.highest_chunk.seed = self.original_seed

		print("Original seed:")
		print(self.original_seed)
		print("Current seed:")
		print(self.get_seed())

		# Trying out a seed tower idea
		# TODO If I want to push chunk generation higher, keeping a tower like this seems like the only way. Offsets can
		#  be stored as int64, but I inevitably have to multiply them by a floating point (well, golden field) matrix,
		#  particularly when I project them to the worldplane to do seed translation. I could write a custom projection
		#  function, but I think the potential benefit is limited. Ultimately, the 64 bit integer would overflow at
		#  around level 28. Now, level 28 is plenty, and I'd pursue the "custom projection function" direction if I had
		#  more confidence in it; but one issue with it is that I'd be inserting a slow function anywhere we want to
		#  translate seeds around.
		#  The seed tower idea, on the other hand: consider each new top-level chunk to be the origin of all offsets on
		#  that level. This should keep offsets extremely small. The added complexity is that converting offsets (and
		#  other coordinates, like chunk centers) from one level to another becomes complex, and needs to be encapsulated.
		#  Offset conversion functions would have to be called from all the same places a custom projection function
		#  would be, but the complexity gain isn't comparable -- just a matter of adding up all offsets from levels that
		#  are going to be traversed in a given translation.
		# self.stacked_seeds = [self.original_seed]
		# self.stacked_seeds_offsets = [self.highest_chunk.offset]
		# while self.highest_chunk.level < 25:
		# 	self.highest_chunk.get_parent()
		# 	self.stacked_seeds.append(self.highest_chunk.seed)
		# 	self.stacked_seeds_offsets.append(self.highest_chunk.offset)
		# print(self.stacked_seeds)
		# print(self.stacked_seeds_offsets)
		# for i in range(len(self.stacked_seeds)):
		# 	print(self.custom_pow(self.deflation_face_axes,i).dot(self.stacked_seeds_offsets[i]).dot(self.squarallel)
		# 		  + pow(-1,i) * self.phipow(-3*i) * self.stacked_seeds[i])

		# hits = self.generate_parents(chunk_num, [0, 0, 0, 0, 0, 0])
		print("getting superchunk")
		self.highest_chunk.get_parent()
		print(time.perf_counter() - starttime)

		# print("Trying to generate super-super-chunk...")
		# print(time.perf_counter() - starttime)
		# superhits = self.generate_parents(hits[0][0], hits[0][1], level=2)
		# print("Got " + str(len(superhits)) + " supersuperchunks")
		# print(time.perf_counter() - starttime)

		#print("getting super-super-chunk")
		#self.highest_chunk.get_parent()
		#print(time.perf_counter() - starttime)

		# supersuperhits = self.generate_parents(superhits[0][0],superhits[0][1],level=3)
		# print("Got "+str(len(supersuperhits))+" supersupersuperchunks")
		# print(time.perf_counter()-starttime)

		# all_supersuperchunks = []
		# for i, offset in supersuperhits:
		#	all_supersuperchunks += self.generate_children(i, offset, level=4)
		# print("Supersuperchunks total: "+str(len(all_supersuperchunks)))
		# superhits = all_supersuperchunks

		# all_superchunks = []
		# for i, offset in superhits:
		# 	all_superchunks += self.generate_children(i, offset,
		# 											  level=3)  # [(int(l[0]),l[1:]) for l in self.generate_children(i,offset,level=3)]
		# print("Superchunks total: " + str(len(all_superchunks)))
		all_superchunks = [self.highest_chunk]#self.highest_chunk.get_children()

		# Draw the valid chunk(s)
		# for superchunk in hits:
		# 	i, offset = superchunk
		# 	multiplier = math.pow(self.phi, 3)
		# 	st = SurfaceTool()
		#
		# 	st.begin(Mesh.PRIMITIVE_LINES)
		# 	st.add_color(Color(1, .2, 1))
		# 	for block in (np.array(self.all_blocks[i][1]) + offset):
		# 		self.draw_block_wireframe(block, st, multiplier)
		# 	st.commit(self.mesh)
		# 	self.mesh.surface_set_material(self.mesh.get_surface_count() - 1, COLOR)
		#
		# 	st.begin(Mesh.PRIMITIVE_LINES)
		# 	st.add_color(Color(0.5, 0, 1))
		# 	for block in (np.array(self.all_blocks[i][0]) + offset):
		# 		self.draw_block_wireframe(block, st, multiplier)
		# 	st.commit(self.mesh)
		# 	self.mesh.surface_set_material(self.mesh.get_surface_count() - 1, COLOR)

		# Draw the valid superchunks?
		# for (i, offset) in superhits:
		# 	multiplier = math.pow(self.phi, 6)
		# 	st = SurfaceTool()
		#
		# 	st.begin(Mesh.PRIMITIVE_LINES)
		# 	st.add_color(Color(.2, 1, 1))
		# 	for block in (np.array(self.all_blocks[i][1]) + offset):
		# 		self.draw_block_wireframe(block, st, multiplier)
		# 	st.commit(self.mesh)
		# 	self.mesh.surface_set_material(self.mesh.get_surface_count() - 1, COLOR)
		#
		# 	st.begin(Mesh.PRIMITIVE_LINES)
		# 	st.add_color(Color(0, 0.5, 1))
		# 	for block in (np.array(self.all_blocks[i][0]) + offset):
		# 		self.draw_block_wireframe(block, st, multiplier)
		# 	st.commit(self.mesh)
		# 	self.mesh.surface_set_material(self.mesh.get_surface_count() - 1, COLOR)

		# Now we draw the blocks inside those chunks.

		# children = chain(*[self.generate_children(i,offset) for i, offset in all_superchunks])
		# Cleverer line above didn't turn out to be faster.
		# children = []
		# for i, offset in all_superchunks:  # all_superchunks:#hits:
		# 	children += self.generate_children(i, offset)
		children = []
		for c in all_superchunks:
			children += c.get_children()
		# These children are the chunks already drawn above, but now
		# accompanied by an appropriate offset and template index so we can draw
		# their blocks. So, test: do the children correspond to the aldready-drawn
		# chunks?
		#		children2 = []
		#		for i, offset in hits:
		#
		print("All " + str(len(children)) + " chunks now generated. Time:")
		print(time.perf_counter() - starttime)

		# Draw these
		# multiplier = 1
		# st = SurfaceTool()
		# st.begin(Mesh.PRIMITIVE_TRIANGLES)
		# st.add_color(Color(r.random(), r.random(), r.random()))

		# List the block coordinates
		# List comp. version faster, but crashes w/ large numbers of blocks.
		# block_comprehension = list(
		# 	chain(*[[block for block in np.concatenate([self.all_blocks[i][0], self.all_blocks[i][1]]) + offset]
		# 			for i, offset in children]))
		# block_comprehension = np.zeros((0,6))
		# for i, offset in children:
		#	block_comprehension = np.concatenate([block_comprehension,self.all_blocks[i][0]])
		# print("All " + str(len(block_comprehension)) + " blocks generated. Time:")
		# print(time.perf_counter() - starttime)

		# Now pass them to the draw function
		# When no drawing occurs, takes about 21 seconds (for-loop version took 40)
		# With drawing, takes about 42 seconds
		def decide(block):
			# print("Entered drawp. "+ str(block[0] + block[1] + block[2]))
			return block[0] + block[1] + block[2] == 0.5

		# list(map(decide, block_comprehension))
		# for block in block_comprehension:
		#	if block[0] + block[1] + block[2] == 0.5:
		#		self.draw_block(block,st,multiplier)
		# for i, offset in children:
		#	for block in (np.concatenate([self.all_blocks[i][0],self.all_blocks[i][1]]) + offset):
		#		if ( block[0] + block[1] + block[3] in [0,1,2]):
		#			self.draw_block(block,st,multiplier)

		# for c in children:
		#	c.draw_mesh()
		print("Done calling draw. Time:")
		print(time.perf_counter() - starttime)
		#print("Chunk overlap measurement with new template alg:")
		#self.measure_chunk_overlap()

		# Add block highlighter as child
		self.add_child(self.block_highlight, "BlockHighlight")

		# test_2 = time.perf_counter()
		# while self.highest_chunk.level < 14:
		# 	self.highest_chunk = self.highest_chunk.get_parent()
		# self.highest_chunk.get_children()
		# print(time.perf_counter() - test_2)

	# if len(children) > 0:
	# 	st.generate_normals()
	# 	st.commit(self.mesh)
	# 	self.mesh.surface_set_material(self.mesh.get_surface_count() - 1, COLOR)
	# print("Mesh updated. Time:")
	# print(time.perf_counter() - starttime)

	def measure_chunk_overlap(self):
		"""
		Checks each chunk template to see how far blocks come into the chunk, which aren't owned by that chunk.
		Distance is a taxi cab distance using the chunk's own axes, as implemented by rhomb_contains_point. I wrote
		this to get a safety margin for the safely_contains_point function. However, it serves as good testing code
		since the result should theoretically not exceed 0.19794.
		:return:
		"""
		# First run got 0.25650393107963126, which is higher than what was in principle expected (0.19793839129906832).
		# Second run, excluded "exterior" blocks which were actually in the interior. Got
		# 0.11524410338055335, which is inside the theoretical bounds. Time to make the search more exhaustive.
		# Third run, back to 0.25650393107963115, and this value was encountered frequently. Ah, I've found a mistake
		# in my distance function. Fourth run, 0.14199511391282338, closer to theoretical and a believable final answer.
		# Fifth run, added just one more point (origin, tip, and one combo point); result unchanged.
		# Sixth run, changing strategy. We ought to get the same measurement using inside blocks as we do with outside,
		# we just have to measure how far they poke *out* instead of *in*. Result: 0.14199511391282327. OK, so we
		# should be able to test more vertices now; iterating through inside blocks saves time. (However, I'm pretty
		# confident in the result.)
		# Seventh run, the definition of inside blocks has changed. Result still 0.14199511391282327.
		# Eighth run, finally added more points. Value changed! 0.18587401723009223
		# Ninth run, decided to add more points along edges, not just corners. 0 . 1 8 5 8 7 4 0 1 7 2 3 0 0 9 2 3 4
		highest = 0
		for template_i in range(len(self.all_blocks)):
			new_chunk = Chunk(self, template_i, [0, 0, 0, 0, 0, 0], 1)
			for block_j in range(len(self.all_blocks[template_i][0])):
				center_3D = self.all_blocks[template_i][0][block_j].dot(self.normalworld.T)
				# If the center is inside the chunk:
				if True:#new_chunk.rhomb_contains_point(center_3D) >= 0:  # 1e-15:
					origin_3D = np.floor(self.all_blocks[template_i][0][block_j]).dot(self.normalworld.T)
					tip_3D = np.ceil(self.all_blocks[template_i][0][block_j]).dot(self.normalworld.T)
					for corner_3D in [origin_3D, tip_3D,
									  np.where([0,0,1], origin_3D, tip_3D),
									  np.where([0,1,0], origin_3D, tip_3D),
									  np.where([0,1,1], origin_3D, tip_3D),
									  np.where([1,0,0], origin_3D, tip_3D),
									  np.where([1,0,1], origin_3D, tip_3D),
									  np.where([1,1,0], origin_3D, tip_3D),
									  origin_3D/2 + np.where([1,0,1], origin_3D, tip_3D)/2,
									  tip_3D/3 + 2*np.where([1,0,1], origin_3D, tip_3D)/3,
									  np.array([(lambda x: origin_3D[0]*x + tip_3D[0]*(1-x))(r.random()),
												(lambda x: origin_3D[1] * x + tip_3D[1] * (1 - x))(r.random()),
												(lambda x: origin_3D[2] * x + tip_3D[2] * (1 - x))(r.random())
												])]:
						distance_to_corner = new_chunk.rhomb_contains_point(corner_3D)
						if distance_to_corner < 0:
							print(-distance_to_corner)
							print(highest)
						if -distance_to_corner > highest:
							highest = -distance_to_corner
		return highest

	def test_templates(self, remove_dupes=False):
		starttime = time.perf_counter()
		possible_blocks = set()
		for blocklayout in self.all_blocks:
			# combined = np.concatenate([blocklayout[0], blocklayout[1]])
			# Right now all we care about is the inner blocks
			combined = blocklayout[0]
			combined = combined * 2
			combined = np.array(np.round(combined), dtype=np.int64)
			combined = [repr(list(x)) for x in combined]
			for block in combined:
				possible_blocks.add(block)
		print("Set up possible blocks list. " + str(len(possible_blocks)) + " occur.")  # 4042
		print(time.perf_counter() - starttime)

		possible_layouts = []
		blocklist = [eval(x) for x in possible_blocks]
		novel_indices = []
		for blocklayout_i in range(len(self.all_blocks)):
			blocklayout = self.all_blocks[blocklayout_i]
			# combined = np.concatenate([blocklayout[0], blocklayout[1]])
			# Right now all we care about is the inner blocks
			combined = blocklayout[0]
			combined = np.round(combined * 2)
			layout = np.any(
				np.all(np.repeat(blocklist, len(combined), axis=0).reshape(-1, len(combined), 6) - combined == 0,
					   axis=2), axis=1)
			novel = True
			for poss in possible_layouts:
				if np.all(layout == poss):
					novel = False
				# debugging.breakpoint()
			if novel:
				possible_layouts.append(layout)
				novel_indices.append(blocklayout_i)
		print("Number of unique layouts according to more careful calculation:")
		print(len(possible_layouts))
		print(time.perf_counter() - starttime)
		if remove_dupes:
			self.all_blocks = [self.all_blocks[i] for i in range(len(self.all_blocks)) if i in novel_indices]
			self.all_constraints = [self.all_constraints[i] for i in range(len(self.all_constraints)) if
									i in novel_indices]
			self.all_chosen_centers = [self.all_chosen_centers[i] for i in range(len(self.all_chosen_centers)) if
									   i in novel_indices]

	def symmetries_search(self):
		# Interesting note: Though all constraints are unique, they consist
		# of a very limited set, of just 11 numbers (6 after absolute value).
		# Well, with no rounding, it's 633 numbers...
		# Despite this, all but 100 of the 4980 constraints can be distinguished
		# by which numbers are present, together with sign. (All can be
		# distinguished if we leave out the rounding.)

		constraint_numsets = []
		numset_counts = []
		numset_members = []
		numset_ids = []
		numset_offsets = []
		constraint_numbers = set()
		for i in range(len(self.all_constraints)):
			match = False
			center = self.possible_centers_live[self.possible_centers.index(self.all_chosen_centers[i])]
			center_axes = 1 - np.array(center - np.floor(center)) * 2
			center_origin = center - np.array(self.deflation_face_axes).T.dot(center_axes) / 2
			center_axis1 = np.array(self.deflation_face_axes[np.nonzero(center_axes)[0][0]])
			center_axis2 = np.array(self.deflation_face_axes[np.nonzero(center_axes)[0][1]])
			center_axis3 = np.array(self.deflation_face_axes[np.nonzero(center_axes)[0][2]])
			chunk_corners = np.array([center_origin,
									  center_origin + center_axis1, center_origin + center_axis2,
									  center_origin + center_axis3,
									  center_origin + center_axis1 + center_axis2,
									  center_origin + center_axis1 + center_axis3,
									  center_origin + center_axis2 + center_axis3,
									  center_origin + center_axis1 + center_axis2 + center_axis3])
			# We consider all translations, since different chunks have the origin
			# at different corners.
			for corner in chunk_corners:
				shift = (-corner).dot(self.normallel.T)
				shifted_constraints = self.all_constraints[i] + np.repeat(
					shift.dot(self.twoface_normals.T).reshape(15, 1), 2, axis=1)
				# str_c = [str(pair) for pair in np.array(self.all_constraints[i])]
				str_c = np.abs(np.round(shifted_constraints, 13)).flatten().tolist()
				for num in str_c: constraint_numbers.add(num)
				str_c.sort()
				str_c = str(str_c)
				if str_c not in set(constraint_numsets):
					constraint_numsets.append(str_c)
					numset_counts.append(1)
					numset_members.append([i])
					numset_offsets.append([corner])
					match = True
				else:
					numset_counts[constraint_numsets.index(str_c)] += 1
					numset_members[constraint_numsets.index(str_c)].append(i)
					numset_offsets[constraint_numsets.index(str_c)].append(corner)
					numset_ids.append(i)
			# print("Match with "+str(self.all_constraints[i]))
		print(str(len(constraint_numbers)) + " constraint numbers.")
		print(str(len(constraint_numsets)) + " constraint numsets.")
		print(str(len([x for x in numset_counts if x == 1])) + " lonely chunks.")

		first_sixer = numset_counts.index(18)

		for i in numset_members[first_sixer]:
			translation = numset_offsets[first_sixer][numset_members[first_sixer].index(i)]
			shift = (-translation).dot(self.normallel.T)
			shifted_constraints = self.all_constraints[i] + np.repeat(shift.dot(self.twoface_normals.T).reshape(15, 1),
																	  2, axis=1)
			print(np.round(shifted_constraints, 5))
			# Waste time so we can print
			# for j in range(5000000):
			#	_ = i + j
			#	_ = _ * _ * _ * _
			print(self.chunk_center_lookup(i) - translation)
			print("(originally " + self.all_chosen_centers[i] + ")")
			print(translation)
			print(i)

		numset_counts.sort()
		print(numset_counts)

		ordered_str = [[str(pair) for pair in np.round(np.array(self.all_constraints[u]))] for u in numset_ids]
		for i in range(len(self.all_constraints)):
			permutation = [ordered_str.index(x) for x in [str(pair) for pair in np.array(self.all_constraints[i])]]
			print(permutation)


class ConstraintTree:
	"""
	Stores a hierarchy of sorted constraints, which can then be queried with a 15-dimensional point.
	The return value, however, is an index into the constraint-set, so this class has to know the
	overall set intended for indexing.
	"""
	sort_dim = 0
	sort_index = 0
	sort_threshhold = 0
	values = []
	is_leaf = False

	def __init__(self):
		sort_dim = 0
		sort_index = 0
		sort_threshhold = 0
		values = []
		is_leaf = False

	@classmethod
	def sort(cls, constraints, constraint_indices, constraint_nums):
		"""
		Takes a set of constraints, along with a set of indices which indicate which constraints will
		be found on this tree. Constructs a tree for fast lookup of the constraints. Also requires
		a list, constraint_nums, of the floats which occur in the entire set of constraints.
		"""
		self = cls()
		self.values = constraint_indices
		if len(constraint_indices) > 1:
			print("Sorting " + str(len(constraint_indices)) + " constraints.")
			# Determine the best way to split up the given constraints. For a given plane,
			# a constraint could fall 'below' it or 'above' it, or could cross through that
			# plane. Crossing through is bad news since those essentially go both below
			# and above, meaning they're not eliminated. What we need to optimize, then,
			# is the product of how many fall below with how many fall above.
			# TODO - although this should never happen, I should think about how to
			# handle values exactly on a boundary.

			below_counts = [[0 for x in dim_nums] for dim_nums in constraint_nums]
			above_counts = [[0 for x in dim_nums] for dim_nums in constraint_nums]

			# TODO The nested for loops really slow things down if the number of
			# constraint_nums goes up, which it does if I try to make constraints more
			# snug. Would be nice to speed this up so I could comfortably test
			# speedups from sharper constraints.
			for i in constraint_indices:
				for dim in range(15):
					start = list(constraint_nums[dim]).index(constraints[i][dim][0])
					end = list(constraint_nums[dim]).index(constraints[i][dim][1])
					# Choices of split up to and including the start number will
					# place this constraint in the 'above' category.
					for j in range(start + 1):
						above_counts[dim][j] += 1
					# Choices of split >= the end number will place this constraint 'below'
					for j in range(end, len(constraint_nums[dim])):
						below_counts[dim][j] += 1
			# Find maximum and store it in the class
			for dim in range(15):
				for num_index in range(len(constraint_nums[dim])):
					if (below_counts[self.sort_dim][self.sort_index] * above_counts[self.sort_dim][self.sort_index]
							< below_counts[dim][num_index] * above_counts[dim][num_index]):
						self.sort_dim = dim
						self.sort_index = num_index
			self.sort_threshhold = constraint_nums[self.sort_dim][self.sort_index]
			if below_counts[self.sort_dim][self.sort_index] * above_counts[self.sort_dim][self.sort_index] == 0:
				# The constraint planes are not differentiating between these two. So, we just leave them
				# both unsorted and declare ourselves a leaf node.
				# TODO: I could add a test here, which makes sure the constraints are nonoverlapping.
				# TODO: Lookup would be *slightly* faster if I sorted these somehow.
				self.is_leaf = True
			# print(str(below_counts[self.sort_dim][self.sort_index])+" below; "
			#	+str(above_counts[self.sort_dim][self.sort_index])+" above; "
			#	+str(len(constraint_indices) - below_counts[self.sort_dim][self.sort_index]
			#	- above_counts[self.sort_dim][self.sort_index])+" between.")
			if not self.is_leaf:
				# Now we just need to do the actual sorting.
				# For these purposes, constraints which are both below and above get
				# handed to *both* child nodes.
				below = []
				above = []
				for i in constraint_indices:
					start = constraint_nums[self.sort_dim].index(constraints[i][self.sort_dim][0])
					end = constraint_nums[self.sort_dim].index(constraints[i][self.sort_dim][1])
					if end > self.sort_index:
						above.append(i)
					if start < self.sort_index:
						below.append(i)
				self.below = ConstraintTree.sort(constraints, below, constraint_nums)
				self.above = ConstraintTree.sort(constraints, above, constraint_nums)
		else:
			# No need to sort, we're a leaf node
			self.is_leaf = True
		return self

	def find(self, point):
		"""
		Accepts a 3D parallel-space point, as represented by its 15 dot products
		with normal vectors to a rhombic triacontahedron's faces. Returns a small
		list of indices to constraints (as listed in self.all_constraints), one
		of which will contain the point.
		"""
		if self.is_leaf:
			return self.values
		if point[self.sort_dim] < self.sort_threshhold:
			return self.below.find(point)
		# Should be fine to include points equal to threshhold on either side;
		# any constraint straddling the threshhold was sent to both.
		if point[self.sort_dim] >= self.sort_threshhold:
			return self.above.find(point)

	@classmethod
	def load(cls, filename="constraint_tree"):
		fs = File()
		fs.open("res://" + filename, fs.READ)
		new_tree = eval(str(fs.get_line()))
		fs.close()
		return new_tree

	def save(self, filename="constraint_tree"):
		fs = File()
		fs.open("res://" + filename, fs.WRITE)
		fs.store_line(repr(self))
		fs.close()

	@classmethod
	def from_dict(cls, description):
		self = cls()
		self.is_leaf = description["is_leaf"]
		if self.is_leaf:
			self.values = description["values"]
		else:
			self.sort_dim = description["sort_dim"]
			self.sort_index = description["sort_index"]
			self.sort_threshhold = description["sort_threshhold"]
			self.below = description["below"]
			self.above = description["above"]
			self.values = self.below.values + self.above.values

		return self

	def __string__(self):
		return "{} with {} values".f(self.__class__.__name__, len(self.values))

	def __repr__(self):
		# Includes all information except:
		# - self.all_constraints
		# - self.constraint_nu
		if self.is_leaf:
			# For leaf nodes, we include self.values, and of course no children
			# or sort parameters
			return "ConstraintTree.from_dict(" + repr({"values": self.values, "is_leaf": self.is_leaf}) + ")"
		else:
			return "ConstraintTree.from_dict(" + repr({"sort_dim": self.sort_dim, "sort_index": self.sort_index,
													   "sort_threshhold": self.sort_threshhold, "is_leaf": self.is_leaf,
													   "below": self.below, "above": self.above}) + ")"


class Chunk:

	def __init__(self, network, template_index, offset, level=1, hypothetical=False):
		self.is_topmost = False
		self.network = network
		self.template_index = template_index
		self.offset = np.array(offset,dtype='int64')
		self.level = level
		self.hypothetical=hypothetical
		# TODO Easy to forget whether self.blocks holds straight template coords or coords with offset. Make the
		#  mistake less easily made. Which *should* it be?
		self.blocks = network.all_blocks[template_index][0]
		self.block_values = np.zeros((len(self.blocks)), dtype=np.int)
		# Copy neighbor info, since we may eventually change it
		self.blocks_neighbor = network.all_blocks_neighbor[template_index]
		self.blocks_neighbor_diag = network.all_blocks_neighbor_diag[template_index]
		self.neighbors_outside_chunk = network.all_neighbors_outside_chunk[template_index]
		self.diag_neighbors_outside_chunk = network.all_diag_neighbors_outside_chunk[template_index]
		# Create our own neighbors array
		self.neighbors = np.array([[[None]*3]*3]*3)
		self.neighbors[1][1][1] = self
		self.neighbors_found = False
		self.diag_neighbors = [self]
		self.diag_neighbors_found = False
		self.parent = None
		self.children = [None] * len(self.blocks)
		self.all_children_generated = False
		if level == 0: self.all_children_generated = True
		self.drawn = False
		self.mesh = None
		self.collision_mesh = None

	def get_parent(self):
		if self.parent is None:
			parents = self.network.generate_parents(self.template_index, self.offset, self.level)  # self.level
			if len(parents) > 1:
				raise Exception(
					"Got more than one parents for a chunk; a way to handle this is currently not implemented.")
			self.parent = Chunk(self.network, parents[0][0], parents[0][1], self.level + 1, self.hypothetical)
			# Sanity test: Any new parent should contain the origin.
			if not self.hypothetical:
				print("Sanity test: is origin inside this? (should be positive)"+str(self.parent.rhomb_contains_point(np.array([0,0,0]))))
			# We have to set ourselves as a child, in the appropriate place
			# TODO Below line took way to long to get right, for two reasons.
			#  - It's easy to forget Chunk.blocks just stores default template positions, not adding in the chunk's
			#    own offset.
			#  - I should still make more utility functions; e.g., something for getting block axes and converting
			#    arbitrary points between chunk level coords.
			chunk_as_block_center = np.round(
				np.array(np.round(np.linalg.inv(self.network.deflation_face_axes)),dtype='int64').dot(
					np.array(np.round(2*self.network.chunk_center_lookup(self.template_index)),dtype='int64')
					+ 2*self.offset - 2*np.array(np.round(self.parent.get_offset(self.level - 1)),dtype='int64'))) / 2.0
			for i in range(len(self.parent.blocks)):
				if np.all(chunk_as_block_center == self.parent.blocks[i]):
					self.parent.children[i] = self
					self.index_in_parent = i
					break
			# TODO Convert into a test
			print("Did block end up parent's child? " + str(self in self.parent.children))
			# There used to be a big block of contingencies here, for trying to repair the tree if the above line
			# turned out false. None of it ever worked though, and I'm not having that problem anymore. If the code
			# is of any interest: it can be found in commits from before June 15th, 2022.
			self.neighbor_centers = self.parent.neighbors_outside_chunk[self.index_in_parent] + self.parent.offset
			self.diag_neighbor_centers = self.parent.diag_neighbors_outside_chunk[self.index_in_parent] + self.parent.offset
			if self.is_topmost:
				print("Adding new top chunk of level " + str(self.level + 1))
				self.is_topmost = False
				self.parent.is_topmost = True
				self.network.highest_chunk = self.parent
				self.parent.seed = parents[0][2]
		return self.parent

	def get_children(self):
		"""
		Returns all direct children, generating any which are not yet generated.
		:return: A list of all children as chunks, in the same order as in the chunk template.
		"""
		# TODO Still struggling with neighbor relationships. Carefully double check here that all neighbors get connected.
		# TODO Occasionally, some children are None even after a get_children call. Why?
		if not self.all_children_generated:
			children = self.network.generate_children(self.template_index, self.offset, self.level)
			if len(children) != len(self.blocks):
				print("MISMATCH BETWEEN CHILDREN AND TEMPLATES")
				print("Children: " + str(len(self.blocks)))
				print("Templates:" + str(len(children)))
			for i in range(len(self.children)):
				if self.children[i] is None:
					self.children[i] = Chunk(self.network, children[i][0], children[i][1], self.level - 1,self.hypothetical)
			self.all_children_generated = True
			# Connect parent, child, and neighbor relationships
			for child_i in range(len(self.children)):
				child = self.children[child_i]
				child.parent = self
				child.index_in_parent = child_i
				# Hand off some generic neighbor information
				# We add our own offset here, which is expressed on the same level of coords as these neighbor offsets
				child.neighbor_centers = self.neighbors_outside_chunk[child_i] + self.offset
				child.diag_neighbor_centers = self.diag_neighbors_outside_chunk[child_i] + self.offset
				# Direct neighbors (those sharing faces)
				# TODO This looks slow; can I pre-compute this?
				axes = np.nonzero(self.blocks[child_i] - np.floor(self.blocks[child_i]))[0]
				for neighbor_i in np.nonzero(self.blocks_neighbor[child_i])[0]:
					neighbor_diff = np.nonzero(self.blocks[child_i] - self.blocks[neighbor_i])[0]
					common_axis = list(set(axes).intersection(set(neighbor_diff)))[0]
					common_axis_index = list(axes).index(common_axis)
					common_axis_sign = np.sign(self.blocks[child_i] - self.blocks[neighbor_i])[common_axis]
					# Not all children are new, but overwriting within-chunk neighbors won't go wrong
					[child.neighbors[:, 1, 1],
					 child.neighbors[1, :, 1],
					 child.neighbors[1, 1, :]]\
						[int(common_axis_index)]\
						[int(common_axis_sign) + 1] \
						= self.children[neighbor_i]
				if len(self.neighbors_outside_chunk[child_i]) == 0:
					child.neighbors_found = True
				if len([chk for chk in child.neighbors.flatten() if chk is not None]) == 7:
					child.neighbors_found = True
				# Diagonal neighbors (those sharing corners)
				for neighbor_i in np.nonzero(self.blocks_neighbor_diag[child_i])[0]:
					# We have to avoid duplicates; children not just created might know neighbors.
					if self.children[neighbor_i] not in child.diag_neighbors:
						child.diag_neighbors.append(self.children[neighbor_i])
				#child.diag_neighbors_found = child._diag_neighbors_complete()
				if len(self.diag_neighbors_outside_chunk[child_i]) == 0:
					child.diag_neighbors_found = True
				total_diag_neighbors = len(np.nonzero(self.blocks_neighbor_diag[child_i])[0]) + len(self.diag_neighbors_outside_chunk[child_i])
				if not child.diag_neighbors_found:
					# Child has diagonal neighbors outside chunk. Can we find them without generating?
					# Note, not all children are necessarily new; some might know of pre-existing neighbors.
					for neighbor_center in child.diag_neighbor_centers:
						# Do we already know this neighbor?
						neighbor_offset = np.array(self.network.deflation_face_axes,dtype='int64').dot(neighbor_center - np.floor(neighbor_center))
						knew_it = len(np.nonzero(np.array([n.offset for n in child.diag_neighbors]) - neighbor_offset)[0]) > 0
						if not knew_it:
							# We have to search within our own *diagonal* neighbors, since (AFAIK) occasionally children
							# can reach out of the chunk and produce unusual neighbor relationships.
							#TODO I think I already verified that this is the case; but, I should make sure, since this
							#  step would be come faster if it's not true.
							for known_neighbor in self.diag_neighbors:
								# Search for the block in question within the template
								center_check = np.nonzero(np.all(self.network.all_blocks[known_neighbor.template_index][0]
																 + known_neighbor.offset - neighbor_center == 0,axis=1))[0]
								if len(center_check) > 0:
									# We've obtained the index of our neighbor
									# If our newly-discovered neighbor is None, it actually wouldn't do any harm to
									# instantiate it.
									if known_neighbor.children[center_check[0]] is None:
										seed = self.network.get_seed(self.level - 1)
										new_neighbor_offset = np.floor(neighbor_center)
										new_neighbor_offset_scaled = np.array(self.network.deflation_face_axes, dtype=int).dot(new_neighbor_offset)
										seed_scaled_translated = (seed - new_neighbor_offset_scaled.dot(self.network.squarallel))
										# Since multiple chunks will exist at the offset, we have to sort through what we get.
										#TODO (This is the main inefficiency here -- we could be instantiating all the chunks
										# with this same origin.)
										valid_indices_at_vertex = self.network.find_satisfied(seed_scaled_translated)
										valid_indices_centers = np.array([self.network.chunk_center_lookup(index) for index in valid_indices_at_vertex])
										# A test where we rescale neighbor_center and compare ends up quite long and illegible. So,
										# doing the trick where we check half-integer dimensions are all different.
										new_neighbor_template_index_index = np.nonzero(np.all((valid_indices_centers + neighbor_center)
																			 - np.round(valid_indices_centers + neighbor_center) != 0, axis = 1))[0][0]
										new_neighbor_template_index = valid_indices_at_vertex[new_neighbor_template_index_index]
										# Comparison test
										# legit_seed = (np.array(self.network.deflation_face_axes,dtype=int).dot(self.network.get_seed(self.level)
										# 															   - known_neighbor.offset.dot(self.network.squarallel))
										# 	  - np.array(self.network.deflation_face_axes,dtype=int).dot(
										# 			np.floor(self.network.all_blocks[known_neighbor.template_index][0][center_check[0]]))
										# 	  .dot(self.network.squarallel))
										# print(known_neighbor.offset + self.network.all_blocks[known_neighbor.template_index][0][center_check[0]])
										# print(neighbor_center)
										# print(legit_seed)
										# print(seed_scaled_translated)
										# legit_numbers = self.network.generate_children(known_neighbor.template_index, known_neighbor.offset, known_neighbor.level)
										# print(legit_numbers[center_check[0]])
										# print((new_neighbor_template_index,new_neighbor_offset_scaled))
										# test_index_offset = self.network.find_satisfied(legit_seed)
										# print(test_index_offset[new_neighbor_template_index_index])
										# print(len(self.network.find_satisfied(seed_scaled_translated)))
										# print()

										known_neighbor.children[center_check[0]] = Chunk(self.network,new_neighbor_template_index,new_neighbor_offset_scaled,self.level-1,self.hypothetical)
										#TODO Look at all this stuff we have to remember to do! Turn this into an accept_child function.
										known_neighbor.children[center_check[0]].index_in_parent = center_check[0]
										known_neighbor.children[center_check[0]].parent = known_neighbor
										# Add this child as a diagonal neighbor, let the other chunk sort out location on that weird grid later.
										known_neighbor.children[center_check[0]].diag_neighbors.append(child)
										known_neighbor.children[center_check[0]].neighbor_centers \
											= known_neighbor.neighbors_outside_chunk[center_check[0]] + known_neighbor.offset
										known_neighbor.children[center_check[0]].diag_neighbor_centers \
											= known_neighbor.diag_neighbors_outside_chunk[center_check[0]] + known_neighbor.offset
									child.diag_neighbors.append(known_neighbor.children[center_check[0]])
				# Hook up 'orthogonal' neighbors
				if not child.neighbors_found:
					# Child has neighbors outside chunk.
					for neighbor_center in child.neighbor_centers:
						# Do we already know this neighbor?
						neighbor_diff = np.nonzero(self.blocks[child_i] + self.offset - neighbor_center)[0]
						common_axis = list(set(axes).intersection(set(neighbor_diff)))[0]
						common_axis_index = list(axes).index(common_axis)
						common_axis_sign = np.sign(self.blocks[child_i] + self.offset - neighbor_center)[common_axis]
						if [child.neighbors[:, 1, 1],
					 		child.neighbors[1, :, 1],
					 		child.neighbors[1, 1, :]]\
								[int(common_axis_index)]\
								[int(common_axis_sign) + 1] is None:
							# Any findable direct neighbor is already in the diagonal neighbors list.
							neighbor_offset = np.array(self.network.deflation_face_axes, dtype='int64').dot(
								neighbor_center - np.floor(neighbor_center))
							already_found = np.nonzero(np.array([n.offset for n in child.diag_neighbors]) - neighbor_offset)[0]
							if len(already_found) > 0:
								[child.neighbors[:, 1, 1],
								 child.neighbors[1, :, 1],
								 child.neighbors[1, 1, :]]\
									[int(common_axis_index)]\
									[int(common_axis_sign) + 1] = child.diag_neighbors[already_found[0]]
			if self.level == 2:
				# Very basic terrain generation
				for child in self.children:
					# We'll use a combination of parallel-space positions to determine heightmap.
					child.heightmap = 10 * (self.get_parent().offset.dot(self.network.normallel.T)[0]
											+ self.offset.dot(self.network.normallel.T)[1]
											+ child.offset.dot(self.network.normallel.T)[2])
					# Fill in blocks below the chosen height. In a fancier version we'd smooth between neighboring chunks.
					child.block_values = (((child.blocks + child.offset).dot(self.network.normalworld.T)[:, 1] < -1)
										  * ((child.blocks + child.offset).dot(self.network.normalworld.T)[:,
											 1] > -2.5))  # child.heightmap - 20
					# Use this line to get a single Conway worm
					#child.block_values = np.all(np.transpose([(child.offset + child.blocks)[:,0] == 0.5, (child.offset + child.blocks)[:,3] == 0.5]), axis=1)
					# This one creates stranger straight lines
					# child.block_values = np.sum(child.offset[:5]) + np.sum(child.blocks[:,:5], axis=1) == 0.0
				# Use below to completely fill chunks
				# if np.any(child.block_values):
				#	child.block_values[:] = True
			if not self.hypothetical:
				# If this is a level 1 chunk, we need to draw the blocks in.
				if self.level == 2:
					# print("Ah, let's draw these in")
					for child in self.children:
						if not child.drawn:
							child.draw_mesh()
				if self.level == 1 and not self.drawn:
					self.draw_mesh()
			legacy_search = False
			if legacy_search and (self.parent is not None):
				# Search sibling chunks for neighbors to the new children.
				# (We also check here for overlap with neighbor chunks.)
				neighbor_list = []
				diag_neighbor_list = []
				neighbor_indices = np.nonzero(self.parent.blocks_neighbor[self.index_in_parent])[0]
				diag_neighbor_indices = np.nonzero(self.parent.blocks_neighbor_diag[self.index_in_parent])[0]
				for neighbor_i in neighbor_indices:
					if self.parent.children[neighbor_i] is not None:
						neighbor = self.parent.children[neighbor_i]
						neighbor_list.append(neighbor)
				for neighbor_i in diag_neighbor_indices:
					if self.parent.children[neighbor_i] is not None:
						neighbor = self.parent.children[neighbor_i]
						diag_neighbor_list.append(neighbor)
				# We've found neighbors which are within the same parent chunk. This chunk may already have
				#  a grandparent, great-grandparent, etc., with completed neighbors calculations for its children.
				#  This means we could look at self.neighbors and find additional neighbor chunks which don't share a
				#  parent with us.
				for neighbor_chunk in self.neighbors.flatten():
					if neighbor_chunk is not None and neighbor_chunk.parent != self.parent:
						# Ah, we haven't considered this one yet!
						# TODO Add Chunk.all_children_found_all_neighbors flag, together with a setter, Chunk.set_neighbors_found()
						#  and Chunk.set_all_children_found_all_neighbors(). The idea is that the setters handle the
						#  recursive checks to keep all parents' all_children_found_all_neighbors flag up to date, and
						#  together these flags help avoid redundant neighbor checks.
						neighbor_list.append(neighbor_chunk)
				for neighbor_chunk in self.diag_neighbors:
					if neighbor_chunk is not None and neighbor_chunk.parent != self.parent:
						diag_neighbor_list.append(neighbor_chunk)
				# List is now complete; simply look through it.
				for neighbor in diag_neighbor_list:
					# TODO Convert from here on into Numpy.
					#  - Add a boolean array to Chunk tracking whether a block has all its neighbors generated, maybe.
					#  - Use the Chunk.blocks coordinate arrays, comparing pairwise all blocks which don't already
					#    have all their neighbors. (Add difference of parents' offsets to self.blocks.)
					#  - Those w/ a difference of zero are dupe chunks.
					#  - Those with a difference of 0.5 in just two dimensions are neighbors.
					#  - Checks for whether any children equal None can happen after that.
					if neighbor.template_index == self.template_index:
						if np.all(neighbor.offset == self.offset):
							print("Warning: Two children of a chunk are identical.")
					for neighbor_child_i in range(len(neighbor.children)):
						neighbor_child = neighbor.children[neighbor_child_i]
						if neighbor_child is not None:
							for child_i in range(len(self.children)):
								child = self.children[child_i]
								if child is not None:
									if child.template_index == neighbor_child.template_index:
										if np.all(child.offset == neighbor_child.offset):
											print(
												"Warning: Duplicate chunk found. Mending network... \n\tThis won't actually work...")
											# TODO Below code was written while trying to figure out how to handle this; it makes
											#  all the pertinent measurements and yet doesn't assign the child to a unique parent.
											#  Get rid of or fix. Fixing would require support for empty slots in che children array
											#  even when all_children_generated == True.
											print("Guilty templates: ")
											print(self.template_index)
											print(neighbor.template_index)
											print("Chunk's position in each parent:")
											np.set_printoptions(precision=None)

											#test_vector = np.array([1, 1, 1, 0, 0, 0]).dot(self.network.worldplane.T)
											test_vector = np.array([1,2,3,0,0,0]).dot(self.network.worldplane.T)
											epsilon = 2e-15
											child_center = self.network.all_blocks[self.template_index][0][child_i]
											neighbor_child_center = self.network.all_blocks[neighbor.template_index][0][neighbor_child_i]
											level = 1
											axes_matrix = self.network.axes_matrix_lookup[self.network.all_chosen_centers[self.template_index]][level]
											neighbor_axes_matrix = self.network.axes_matrix_lookup[self.network.all_chosen_centers[neighbor.template_index]][level]
											child_center_in_world = child_center.dot(self.network.worldplane.T)
											neighbor_child_center_in_world = neighbor_child_center.dot(self.network.worldplane.T)
											child_center_in_chunk_axes = np.array(child_center_in_world).dot(axes_matrix) - 0.5
											neighbor_child_center_in_chunk_axes = np.array(neighbor_child_center_in_world).dot(
												neighbor_axes_matrix) - 0.5
											print(child_center_in_chunk_axes)
											print(neighbor_child_center_in_chunk_axes)

											child_dist_from_center = np.abs(child_center_in_chunk_axes)
											neighbor_child_dist_from_center = np.abs(neighbor_child_center_in_chunk_axes)
											test_vector_in_chunk_axes = test_vector.dot(axes_matrix)
											test_vector_in_neighbor_chunk_axes = test_vector.dot(neighbor_axes_matrix)

											print("Ownership calc from current chunk:")
											print(test_vector_in_chunk_axes)
											face_indices = np.nonzero(np.all(np.array(
												[child_dist_from_center >= 0.5 - epsilon, child_dist_from_center <= 0.5 + epsilon]),
																			 axis=0))[0]
											face_tests = []
											for face_i in face_indices:
												# Which direction is the face?
												face_sign = np.sign(child_center_in_chunk_axes[face_i])
												if test_vector_in_chunk_axes[face_i] * face_sign > 0:
													# Test vector points out of this face, so, out of chunk.
													face_tests.append(False)
												else:
													face_tests.append(True)

											print(face_indices)
											print(face_tests)

											print("Ownership calc from neighbor chunk:")
											print(test_vector_in_neighbor_chunk_axes)
											face_indices = np.nonzero(np.all(np.array(
												[neighbor_child_dist_from_center >= 0.5 - epsilon,
												 neighbor_child_dist_from_center <= 0.5 + epsilon]),
												axis=0))[0]
											face_tests = []
											for face_i in face_indices:
												# Which direction is the face?
												face_sign = np.sign(neighbor_child_center_in_chunk_axes[face_i])
												if test_vector_in_neighbor_chunk_axes[face_i] * face_sign > 0:
													# Test vector points out of this face, so, out of chunk.
													face_tests.append(False)
												else:
													face_tests.append(True)

											print(face_indices)
											print(face_tests)

											lowered_center = self.network.custom_pow(
												np.array(self.network.deflation_face_axes),
												self.level - 1).dot(
												self.get_offset(level=self.level - 1) + self.blocks[child_i])
											lowered_origin = self.network.custom_pow(
												np.array(self.network.deflation_face_axes),
												self.level - 1).dot(
												child.get_offset(level=self.level - 1))
											block_axes = \
											np.nonzero(self.blocks[child_i] - np.floor(self.blocks[child_i]))[0]
											lowered_testpoint = self.network.custom_pow(
												np.array(self.network.deflation_face_axes),
												self.level - 1).dot(
												child.get_offset(level=self.level - 1) + 1.0 * np.eye(6)[
													block_axes[0]] + 0.0 * np.eye(6)[block_axes[1]] + 0.0 *
												np.eye(6)[block_axes[2]])
											lowered_testpoint2 = self.network.custom_pow(
												np.array(self.network.deflation_face_axes),
												self.level - 1).dot(
												child.get_offset(level=self.level - 1) + 0.0 * np.eye(6)[
													block_axes[0]] + 1.0 * np.eye(6)[block_axes[1]] + 0.0 *
												np.eye(6)[block_axes[2]])
											self_dist_center = self.rhomb_contains_point(
												lowered_center.dot(self.network.worldplane.T))
											neighbor_dist_center = neighbor.rhomb_contains_point(
												lowered_center.dot(self.network.worldplane.T))
											self_dist_origin = self.rhomb_contains_point(
												lowered_origin.dot(self.network.worldplane.T))
											neighbor_dist_origin = neighbor.rhomb_contains_point(
												lowered_origin.dot(self.network.worldplane.T))
											self_dist_testpoint = self.rhomb_contains_point(
												lowered_testpoint.dot(self.network.worldplane.T))
											neighbor_dist_testpoint = neighbor.rhomb_contains_point(
												lowered_testpoint.dot(self.network.worldplane.T))
											self_dist_testpoint2 = self.rhomb_contains_point(
												lowered_testpoint2.dot(self.network.worldplane.T))
											neighbor_dist_testpoint2 = neighbor.rhomb_contains_point(
												lowered_testpoint2.dot(self.network.worldplane.T))
											if self_dist_origin == neighbor_dist_origin:
												# print("Origin distance: "+str(self_dist_origin))
												if self_dist_testpoint == neighbor_dist_testpoint:
													# print("Test1 distance: " + str(self_dist_testpoint))
													if self_dist_testpoint2 == neighbor_dist_testpoint2:
														print("Your scheme will never work!")
											self.children[child_i] = neighbor_child
										else:
											# Template indices are the same, but offsets differ. This seems like
											# it's very unlikely, so could be a bad sign, but it's perfectly possible.
											pass
									else:
										# Template indices differ.
										# TODO Could check whether these are overlapping despite the different template.
										# Check whether these are direct neighbors. Neighbors have exactly two differing
										# 6D coordinates, and the difference is 0.5.
										difference = (self.offset + self.blocks[child_i]) \
													 - (neighbor.offset + neighbor.blocks[neighbor_child_i])
										if np.sum(np.abs(difference)) == 1 and len(np.nonzero(difference)[0]) == 2:
											axes = np.nonzero(self.blocks[child_i] - np.floor(self.blocks[child_i]))[0]
											neighbor_axes = np.nonzero(neighbor.blocks[neighbor_child_i]
													- np.floor(neighbor.blocks[neighbor_child_i]))[0]
											neighbor_diff = np.nonzero(difference)[0]
											common_axis = list(set(axes).intersection(set(neighbor_diff)))[0]
											neighbor_common_axis = list(set(neighbor_axes).intersection(set(neighbor_diff)))
											common_axis_index = list(axes).index(common_axis)
											neighbor_common_axis_index = list(neighbor_axes).index(neighbor_common_axis)
											common_axis_sign = np.sign(difference)[common_axis]
											neighbor_common_axis_sign = np.sign(difference)[neighbor_common_axis]
											[child.neighbors[:, 1, 1],
											 child.neighbors[1, :, 1],
											 child.neighbors[1, 1, :]][int(common_axis_index)][
												int(common_axis_sign) + 1] = neighbor_child
											[neighbor_child.neighbors[:, 1, 1],
											 neighbor_child.neighbors[1, :, 1],
											 neighbor_child.neighbors[1, 1, :]][int(neighbor_common_axis_index)][
												int(neighbor_common_axis_sign) + 1] = child
											if len(np.nonzero(child.neighbors)[0]) == 7:
												child.neighbors_found = True
											if len(np.nonzero(neighbor_child.neighbors)[0]) == 7:
												neighbor_child.neighbors_found = True
										# Now check whether they are diagonal neighbors.
										if np.sum(np.abs(difference)) <= 3 and np.max(np.abs(difference)) <= 1:
											if np.max(np.abs(difference)) == 0:
												raise Exception("\nDuplicate chunk found! I'm not even going to mend the network\n")
											if neighbor_child not in child.diag_neighbors:
												child.diag_neighbors.append(neighbor_child)
												child.diag_neighbors_found = child._diag_neighbors_complete()
											if child not in neighbor_child.diag_neighbors:
												neighbor_child.diag_neighbors.append(child)
												neighbor_child.diag_neighbors_found = neighbor_child._diag_neighbors_complete()
		return self.children

	def get_diag_neighbors(self, generate=False):
		"""
		Returns a list of all known neighbors sharing at least a corner with the chunk.
		:param generate: If True, the call will generate new chunks as necessary in order to return all diagonal neighbors.
		:return: A list of chunks.
		"""
		if self.diag_neighbors_found or not generate:
			return self.diag_neighbors
		# TODO How can I implement this? There's no exact count to be had, to verify we've got all the neighbors. Ideas:
		#  1) Create templates which apply to individual corners (IE, with seed translated so the corner is origin)
		#     and list precisely the blocks neighboring that corner and nothing else.
		#  2) Consider the dual of a corner of this chunk. Corners of this polyhedron correspond to neighbors. Edges
		#     correspond to shared faces between neighbors. Faces of the shape correspond to shared edges between
		#     neighbors. Faces can be up to seven-sided, I believe. But the corners should always connect three
		#     faces (and three edges), since every neighbor of our chosen point is a rhombohedron, with three faces
		#     touching the point. If any neighbor of our chosen point is missing, we can tell because some other
		#     neighbor of our chosen point will share faces with less than three.
		#  3) At the moment, all chunk templates contain blocks (the os_blocks) which extent outside the chunk, and
		#     even blocks which only touch the chunk at one point. This halo of extra blocks should theoretically touch
		#     every diagonal neighbor. And if it doesn't, that would at least be interesting to know. So: the strategy
		#     I have in mind would be to create a bunch of 'hypothetical children' like increment_search used to;
		#     simply create new Chunk objects with their offsets given by the os_blocks. When trying to find a block's
		#     diagonal neighbors, these chunks would be hypothetical sub-blocks. Next, we need to make sure each
		#     hypothetical chunk is "safely inside" some parent of the current chunk tree, adding a new top-level chunk
		#     if necessary. Then the hypothetical chunks will have direct parents which would fit on the tree. We just
		#     have to instantiate hypothetical parents until we find a linking point. Finally, we can simply declare the
		#     direct parents of our hypothetical children (well, their non-hypothetical counterparts) to be the proper
		#     set of neighbors (ie, neighbors including diagonals). This set has the relevant property of covering all
		#     blocks in the template. If it misses some occasional diagonals, I may need to re-generate my templates.

		# Attempting to do suggestion #3.

		# Check for existing neighbors
		for neighbor in self.neighbors.flatten():
			if neighbor is not self:
				if neighbor not in self.diag_neighbors:
					self.diag_neighbors.append(neighbor)
		# # We can get all os_children, but mixed with is_children.
		# all_possible_children = self.network.generate_children(self.template_index, self.offset, self.level, True)
		# all_is_children = self.network.generate_children(self.template_index, self.offset, self.level, False)
		# # We'll get rid of the is_children by comparing with our own, and also, remove any that
		# # correspond to children of already-known neighbors.
		# all_known_children = all_is_children
		# for neighbor in self.diag_neighbors:
		# 	if neighbor is not None:
		# 		# There's no reason to worry about calling neighbor.get_children() because we're not actually worried
		# 		# about the children, just the neighbor.
		# 		all_known_children = all_known_children + self.network.generate_children(neighbor.template_index, neighbor.offset, neighbor.level)
		# actual_child_templates = [child[0] for child in all_known_children]
		# actual_child_offsets = [child[1] for child in all_known_children]
		# possible_os_children = []
		# for child in all_possible_children:
		# 	found_inside = False
		# 	template_matches = np.nonzero(np.array(actual_child_templates) == child[0])[0]
		# 	for match_i in template_matches:
		# 		if np.all(actual_child_offsets[match_i] == child[1]):
		# 			found_inside = True
		# 			break
		# 	if not found_inside:
		# 		possible_os_children.append(child)
		# # Now the list has just children outside known neighbors (and outside self).
		# possible_os_chunks = [Chunk(self.network, child[0], child[1], self.level - 1, True) for child in
		# 						 possible_os_children]
		# # We'll have a lot of hypothetical chunks to clean up
		# def cleanup(possible_os_chunks=possible_os_chunks):
		# 	for chunk in possible_os_chunks:
		# 		del chunk
		# 	del possible_os_chunks
		#
		# # Now, these possible_os_chunks are below the level we really care about; we're just using them to define our
		# # 'diagonal neighbors'.
		# Now that we have pre-computed diagonal neighbors, we don't need to create hypothetical children.
		# We will need a parent though, to get that information.
		self.get_parent()
		#hypothetical_neighbors = [chunk.get_parent() for chunk in possible_os_chunks]
		if len(self.diag_neighbor_centers) == 0:
			return self.diag_neighbors
		# Check which neighbors we already know.
		unknown_neighbor_indices = []
		diag_neighbor_offsets = np.floor(self.diag_neighbor_centers)
		diag_neighbor_offsets_scaled = np.array(self.network.deflation_face_axes,dtype='int64').dot(diag_neighbor_offsets.T).T
		found_neighbor_offsets = np.array([chunk.offset for chunk in self.diag_neighbors if chunk is not None])
		for center_i in range(len(self.diag_neighbor_centers)):
			known_index = np.nonzero(np.all((diag_neighbor_offsets_scaled[center_i] - found_neighbor_offsets) == 0,axis=1))[0]
			if len(known_index) == 0:
				unknown_neighbor_indices.append(center_i)
		unknown_neighbor_centers = self.diag_neighbor_centers[unknown_neighbor_indices]
		if len(unknown_neighbor_centers) == 0:
			self.diag_neighbors_found = True
			return(self.diag_neighbors)
		diag_neighbors = self.find_chunks_from_blockscale_centers(unknown_neighbor_centers, self.level)
		print("\n\nAdded "+str(len(diag_neighbors))+" neighbors.\n\n")
		for chunk in diag_neighbors:
			if chunk not in self.diag_neighbors:
				self.diag_neighbors.append(chunk)
		if len(self.diag_neighbors) == 0:
			print("Something went wrong finding neighbors... got none??")
			print(diag_neighbors)
		self.diag_neighbors_found = True
		return self.diag_neighbors

	def find_chunks_from_blockscale_centers(self, unknown_centers, level):
		"""
		Generative chunk search, optimized to find several chunks which are clustered together, given known center
		 coordinates, like those provided by Chunk.neighbor_offsets.
		:param unknown_centers: "blockscale" centers of chunks to be found. IE, presented on the scale in which the
		 chunks to be found are just one unit across.
		:param level: Level of chunks that are to be found.
		:return: A list of chunks, corresponding to the unknown_centers, if they are valid with the current seed.
		"""
		unknown_offsets = np.floor(unknown_centers)
		unknown_offsets_scaled = np.array(self.network.deflation_face_axes, dtype='int64').dot(unknown_offsets.T).T
		translated_seeds = self.network.get_seed(self.level) - unknown_offsets_scaled.dot(self.network.squarallel)
		unknown_templates = []
		for unknown_i in range(len(unknown_centers)):
			hits = self.network.find_satisfied(translated_seeds[unknown_i])
			centers = np.array([self.network.chunk_center_lookup(index) for index in hits])
			index_in_hits = np.nonzero(np.all((centers + unknown_centers[unknown_i])
											  - np.round(
				centers + unknown_centers[unknown_i]) != 0, axis=1))[0][0]
			unknown_templates.append(hits[index_in_hits])

		# TODO I could switch to manipulating (index, offset) pairs instead of hypothetical chunks.
		hypothetical_blocks = [Chunk(self.network, unknown_templates[i], unknown_offsets_scaled[i], self.level, hypothetical=True)
							   for i in range(len(unknown_centers))]

		def cleanup(hypothetical_blocks=hypothetical_blocks):
			for chunk in hypothetical_blocks:
				del chunk
			del hypothetical_blocks

		hypothetical_blocks_unique = []
		hypothetical_blocks_unique_strings = []
		# Need to filter out the inevitable duplicates
		for chunk in hypothetical_blocks:
			chunk_string = str((chunk.template_index, chunk.offset))
			if chunk_string not in hypothetical_blocks_unique_strings:
				hypothetical_blocks_unique_strings.append(chunk_string)
				hypothetical_blocks_unique.append(chunk)
		to_cleanup = []
		for i in range(len(hypothetical_blocks)):
			if hypothetical_blocks[i] not in hypothetical_blocks_unique:
				to_cleanup.append(hypothetical_blocks[i])
		cleanup(to_cleanup)
		del hypothetical_blocks
		hypothetical_blocks = hypothetical_blocks_unique

		parent_stack = [self]
		while parent_stack[-1].parent is not None:
			parent_stack.append(parent_stack[-1].parent)
		parent_stack_templates = [p.template_index for p in parent_stack]

		parent_safely_contains_check = [[c.safely_contains_point(target.get_center_position()) for c in parent_stack] for target in hypothetical_blocks]

		while not np.all(np.any(parent_safely_contains_check,axis=1)):
			print("Highest parent does not safely contain target block.")
			parent_stack.append(parent_stack[-1].get_parent())
			print("Added new parent, testing again.")
			parent_safely_contains_check = [[c.safely_contains_point(target.get_center_position()) for c in parent_stack] for target in
											hypothetical_blocks]

		# Make child_parent_stacks each higher until they meet parent_stack somewhere.
		# A more idealistic version of this algorithm might try to make each child_parent_stack higher until it collides
		#  with the real chunk tree *anywhere*. But I think focusing on parent_stack is a good compromise.
		child_parent_stacks = [[possible_child] for possible_child in hypothetical_blocks]
		matching_ancestors = [None]*len(hypothetical_blocks)
		for stack_height in range(len(parent_stack)):
			for hyp_i in range(len(hypothetical_blocks)):
				if matching_ancestors[hyp_i] is None:
					child_parent_stacks[hyp_i].append(child_parent_stacks[hyp_i][-1].get_parent())
					# Check if we've generated a duplicate
					# (We usually will generate a duplicate. However, how would we avoid this? If we call
					# generate_parent to get an offset and template index for comparison, we may as well call get_parent.
					# TODO The more practical option would be to look though parents already generated at this level, and
					#  see if their children (checked within their templates, not generate_children) are a match for
					#  child_parent_stacks[hyp_i]. But at that point we're making lots of subtractions to check; would
					#  it be worth it?
					for hyp_j in range(hyp_i):
						if len(child_parent_stacks[hyp_j]) == len(child_parent_stacks[hyp_i]):
							if child_parent_stacks[hyp_i][-1].template_index == child_parent_stacks[hyp_j][-1].template_index:
								if np.all(child_parent_stacks[hyp_i][-1].offset == child_parent_stacks[hyp_j][-1].offset):
									# Duplicate.
									duplicate = child_parent_stacks[hyp_i][-1]
									child_parent_stacks[hyp_i][-1] = child_parent_stacks[hyp_j][-1]
									child_parent_stacks[hyp_i][-2].parent = child_parent_stacks[hyp_j][-1]
									del duplicate
									break
					new_parent = child_parent_stacks[hyp_i][-1]
					if new_parent.template_index in parent_stack_templates:
						possible_matches = [parent_stack[template_match] for template_match in
											np.nonzero(np.array(parent_stack_templates) == new_parent.template_index)[0]]
						for possible_match in possible_matches:
							if np.all(possible_match.offset == new_parent.offset):
								# We've got a match.
								matching_ancestors[hyp_i] = possible_match
								continue
		united_test = [ancestor == None for ancestor in matching_ancestors]
		if np.any(united_test):
			# This originally was happening because, indexing a loop incorrectly, I was always skipping just 1 chunk.
			print("Failed to connect "+str(len(np.nonzero(united_test)[0]))+" sought offsets with existing hierarchy.")
			print(united_test)
			print((self.template_index, self.offset))
			print([str((chunk.template_index, chunk.offset)) for chunk in hypothetical_blocks])
			raise Exception("Failed to connect "+str(len(np.nonzero(united_test)[0]))+" sought offsets with existing hierarchy.")
		for stack_i in range(len(child_parent_stacks)):
			# We want to step from large to small.
			child_parent_stacks[stack_i].reverse()
			# We don't need the largest hypothetical parent since we already stored its match.
			#child_parent_stacks[stack_i] = child_parent_stacks[stack_i][1:]

		# TODO At this point, everything's getting hookep up every time here. I could switch to an approach where I
		#  don't call get_children, and instead, when a matching child doesn't already exist, I could have the lowest
		#  match adopt the remaining stack of hypothetical chunks.
		lowest_matches = [chunk for chunk in matching_ancestors]
		match_counts = [0]*len(lowest_matches)
		print("Chunk center search: evaluating all parent stacks.")
		# We start at 1, since we don't need the largest hypothetical parent -- we already stored its match.
		for i in range(1,max([len(stack) for stack in child_parent_stacks])):
			# We'll ignore stacks that are over with already, but include them for ease of indexing.
			# print("Stack is about to complain about index.")
			# print("i: "+str(i))
			# print("len(stack): "+str([len(stack) for stack in child_parent_stacks]))
			# print("min: "+str([min(i,max(len(stack)-1,0)) for stack in child_parent_stacks]))
			hypotheticals_to_find = [stack[min(i,max(len(stack)-1,0))] for stack in child_parent_stacks]
			real_chunks_to_search = lowest_matches
			#TODO This loop is repeating effort whenever some chunk and its child appear multiple times.
			for j in range(len(child_parent_stacks)):
				if len(child_parent_stacks[j]) > i:
					possible_chunk = hypotheticals_to_find[j]
					lowest_match = real_chunks_to_search[j]
					# Sometimes lowest_match is None, because no ancestor got united.
					if lowest_match is None:
						continue
					sift_amongst = [chunk for chunk in lowest_match.get_children() if chunk is not None]
					sifted_template = [c.template_index == possible_chunk.template_index for c in sift_amongst]
					sifted_offset = [np.all(c.offset == possible_chunk.offset) for c in sift_amongst]
					if not np.any(sifted_template) or not np.any(sifted_offset):
						print("Unable to merge entire parent stack while finding chunk by center. Matched " + str(match_counts[j]) + ".")
						continue
					# We've got a match
					lowest_matches[j] = sift_amongst[np.nonzero(np.array(sifted_template) * np.array(sifted_offset))[0][0]]
					match_counts[j] += 1
		chunks_located = []
		for match_i in range(len(match_counts)):
			if match_counts[match_i] == len(child_parent_stacks[match_i]):
				chunks_located.append(lowest_matches[match_i])
		cleanup()
		for stack in child_parent_stacks:
			cleanup(stack)
		return chunks_located

	def _diag_neighbors_complete(self):
		"""
		True if all diagonal neighbors have been found; otherwise, false.
		:return: A boolean.
		"""
		# TODO The idea here is to do a careful check, not just look at the variable.
		#  Two methods that might work for this:
		#  1) Create templates which apply to individual corners (IE, with seed translated so the corner is origin)
		#     and list precisely the blocks neighboring that corner and nothing else.
		#  2) Consider the dual of a corner of this chunk. Corners of this polyhedron correspond to neighbors. Edges
		#     correspond to shared faces between neighbors. Faces of the shape correspond to shared edges between
		#     neighbors. Faces can be up to seven-sided, I believe. But the corners should always connect three
		#     faces (and three edges), since every neighbor of our chosen point is a rhombohedron, with three faces
		#     touching the point. If any neighbor of our chosen point is missing, we can tell because some other
		#     neighbor of our chosen point will share faces with less than three.
		pass

	def get_neighbors(self, generate=False):
		"""
		Returns a 3x3x3 array holding between 1 and 7 Chunk objects (the rest are None). The center object will be self,
		and positions with just one nonzero coordinate will hold a neighbor. Neighbors with opposite coordinates within
		the array will be on opposite sides of the chunk.
		:param generate: False by default. If set to True, the neighbors will be generated, so that the returned array
		will be guaranteed to contain seven chunks.
		:return: Returns a 3x3x3 array holding between 1 and 7 Chunk objects (the rest are None). The center object will be self,
		and positions with just one nonzero coordinate will hold a neighbor. Neighbors with opposite coordinates within
		the array will be on opposite sides of the chunk.
		"""
		if self.neighbors_found or not generate:
			return self.neighbors
		# Check for existing neighbors
		self.get_parent()
		if len(self.neighbor_centers) == 0:
			return self.neighbors
		# Check which neighbors we already know.
		unknown_neighbor_indices = []
		neighbor_offsets = np.floor(self.neighbor_centers)
		neighbor_offsets_scaled = np.array(self.network.deflation_face_axes,dtype='int64').dot(neighbor_offsets.T).T
		found_neighbor_offsets = np.array([chunk.offset for chunk in self.neighbors.flatten() if chunk is not None])
		for center_i in range(len(self.neighbor_centers)):
			known_index = np.nonzero(np.all((neighbor_offsets_scaled[center_i] - found_neighbor_offsets) == 0,axis=1))[0]
			if len(known_index) == 0:
				unknown_neighbor_indices.append(center_i)
		unknown_neighbor_centers = self.neighbor_centers[unknown_neighbor_indices]
		if len(unknown_neighbor_centers) == 0:
			self.neighbors_found = True
			return(self.neighbors)
		neighbors = self.find_chunks_from_blockscale_centers(unknown_neighbor_centers, self.level)
		print("\n\nAdded "+str(len(neighbors))+" neighbors.\n\n")
		# We'll depend on get_children() to put the neighbors in the right spot in the neighbors array...
		# for chunk in neighbors:
		# 	if chunk not in self.neighbors.flatten():
		# 		self.neighbors.append(chunk)
		if len([chunk for chunk in self.neighbors.flatten() if chunk is not None]) != 7:
			print("Something went wrong finding neighbors... got "
				  +str(len([chunk for chunk in self.neighbors.flatten() if chunk is not None])))
			print(neighbors)
		else:
			self.neighbors_found = True
		return self.neighbors

	def get_existing_children(self):
		"""
		Note; these are typically not in an order matching self.blocks_neighbor.
		:return:
		"""
		return [child for child in self.children if child != None]

	def rhomb_contains_point(self, point):
		"""
		Quick check for point containment using just the rhombohedral shape of the chunk. Bear in mind a chunk's
		sub-chunks or blocks can extend out from the rhombohedron or not cover the entire rhombohedron (where neighbor
		chunks' sub-chunks/blocks extend in). Use safely_contains_point to check for certain.
		:param point: The point to be checked.
		:return: A signed distance function which is positive when the point lies inside the chunk; the distance from
		the point to the nearest face of the rhombohedron (scaled so that the center of the chunk is at distance 0.5).
		Suitable for checking whether a sphere falls fully within the rhombohedron. Not suitable for checking for
		spherical overlap, since the negative values are not accurate Euclidean distances.
		"""
		# TODO I will often want to do this in large contiguous batches of chunks, wherein there are probably good
		# 	search strategies; or at least I could probably feed all the block coordinates to a single Numpy command
		# 	and do the math much more quickly. One search strategy might be to use neighbor relations to move along
		# 	Conway worms, starting perhaps from some good guess; but then I need to store enough structural info to
		# 	make Conway worms easy to traverse. Also it would be nice to have enough structural info to quickly generate
		# 	a good guess - grabbing a lattice point with at least one 6D coordinate already close.
		# 	Hmm, doing the Conway worm traversal requires that the set of chunks being searched be "Conway convex",
		# 	with all shortest Conway worm paths falling entirely in the set. Would be fun to have a "Conway closure"
		# 	function, for making smoothed shapes in terrain gen.
		# Historical note: the above comment led to a mathematical tangent, me emailing Peter Hilgers, and
		# my collaborating with him and Anton Shutov on a paper.

		# If level < 10, we have a lookup table of the matrices.
		if self.level < 10:
			axes_matrix = self.network.axes_matrix_lookup[self.network.all_chosen_centers[self.template_index]][
				self.level]
		else:
			# Determine orientation via template's center point.
			ch_c = np.array(self.network.chunk_center_lookup(self.template_index))
			# Chunks work opposite to blocks - the axes which are integer at their center are the ones in which the chunk
			# has positive size.
			axes = np.nonzero(ch_c - np.floor(ch_c) - 0.5)[0]
			# Convert point into the rhombohedron's basis for easy math
			# TODO Should use the golden field object to calculate these accurately; matrix inverse will introduce error.
			# TODO Also there's an array self.network.axes_matrix_lookup which contains precomputed matrices.
			axes_matrix = np.linalg.inv(self.network.worldplane.T[axes] * self.network.phipow(3 * self.level))
		worldplane_chunk_origin = self.get_offset(0).dot(self.network.worldplane.T)
		target_coords_in_chunk_axes = (point - worldplane_chunk_origin).dot(axes_matrix) - 0.5
		# To measure distance from closest face-plane, we take the minimum of the absolute value.
		dist_from_center = np.abs(target_coords_in_chunk_axes)
		return np.min(0.5 - dist_from_center)

	def get_offset(self, level=0):
		"""
		Returns the chunk's offset, scaled appropriately for the requested level.
		:param level: Optional argument, the level to scale the offset to. The default is zero, referring to block level;
		note that this convention means self.offset will differ from self.get_offset(self.level). A chunk's stored offset
		is equal instead to self.get_offset(self.level - 1).
		:return: A numpy array, giving 6D coordinates of the chunk's location.
		"""
		# TODO Add documentation focused on avoiding floating point error.
		# return np.linalg.matrix_power(np.array(self.network.deflation_face_axes), (self.level-1) - level).dot(self.offset)
		return self.network.custom_pow(np.array(self.network.deflation_face_axes), self.level - 1 - level).dot(
			self.offset)

	def get_center_position(self):
		"""
		Returns a chunk's center's position in 3D, in "level 1" coordinates.
		:return:
		"""
		center_6D = self.network.chunk_center_lookup(self.template_index) + self.offset
		# center_6D = self.network.all_blocks[self.get_parent().template_index][0][
		# 				self.get_parent().children.index(self)] + self.get_parent().get_offset(self.level)
		# Convert to level 0
		center_6D = self.network.custom_pow(np.array(self.network.deflation_face_axes), self.level).dot(center_6D)
		return center_6D.dot(self.network.worldplane.T)

	def find_triacontahedron(self):
		"""
		Locates a triacontahedron within the chunk.
		:return: None if no triacontahedron is found; otherwise, a set of 20 sub-chunks forming one.
		"""
		# TODO Not the best place for this. Do I want it to operate on arbitrary contiguous clumps of chunks? Or
		# 	maybe return triacontahedra of a target level near a target point?

		# Triacontahedra are sets of tiles which all come from 3-faces of the same hypercube. Hypercubes have centers
		# with all-half-integer values. So the procedure is to look for large sets of tile centers whose half-integer
		# positions all equal those of the same central hypercube, and whose integer positions are only away from that
		# center by 0.5. Speed isn't too important for this - its main use case right now is setting up the starting
		# planet and moon. But if I use it for creating decorative trees and other terrain features later, I'll need
		# to worry a bit more about speed.
		pass

	def safely_contains_point(self, point, block_level=0):
		"""
		Returns true if the point can definitely be said to be inside the chunk - meaning it would be inside some block
		which is a descendant of the chunk. This function generates false negatives, and doesn't actually search
		existing children; it's meant as the check one would run to decide whether to search children.
		:param point: The point to be checked, converted into block-level worldplane coordinates.
		:param block_level: At and below this level, no safety margin is used since blocks genuinely have rhombohedral boundaries.
		:return: Boolean.
		"""
		# TODO Determine what the safe margins are. There are lots of clever things I could do, but this function
		#  mainly has to be fast. Also: the logic of _child_chunk_search is based on sorting children by their
		#  probability of containing a point, and for it to work safely_contains_point and might_contain_point need
		#  to be merely based on cutoffs in the value of some norm. So if I make any improvements here, I may need to
		#  make a new norm function corresponding with that (which also has to be fairly fast).
		# Brainstorming:
		# - Chunk corners always contain blocks aligned with the chunk axes, so those areas are safe. Actually any of the
		# 		"always included" blocks which are part of every chunk could be tested.
		# - I could take an intersection of all chunk templates and then create a convex interior of it with not too many faces.
		# - Function could depend on self.level, using the chunk's template itself when level = 1, and growing more cautious higher up.
		# - I could search through all templates for vertices which are missing a neighbor (ie, one of the blocks touching
		#		that vertex is outside the template), and take note of the distance of that vertex into the chunk as
		#		scored by rhomb_contains_point. Any point further in than that would be safely in the chunk. -Ive done this now
		# - I could do the above, but use two fast but differently-shaped distance metrics. Current rhomb_contains function
		# 		is like L_inf norm, but I could use taxi cab norm as well; combining the two is like using a cube and
		# 		an octahedron together as a nonconvex boundary.
		# - For higher confidence I should do the exhaustive template search thing using, essentially, superchunks
		# 		instead of chunks.
		if self.level <= block_level:
			# At block level, rhomb_contains_point is the true containment. Not sure if any
			return self.rhomb_contains_point(point) > 0
		# self.rhomb_contains_point gives us a value of 0 at rhombus boundary and 0.5 at center.
		# We know that at worst, a prolate rhomb could point directly into a face (but, this never actually happens!) and
		# that rhomb could be almost halfway inside the chunk. It turns out that with side length equal to one, a
		# prolate rhomb has a diagonal of sqrt((1/100.0)*(56*sqrt(5)+156)).
		# Changed from theoretical value 0.1979 to value 0.1420 below based on brute force examination of templates
		# TODO Value of 0.14199511391282338 was not completely reliable; parent would 'safely contain' target but
		#  children may not contain it. As far as I've observed, the closest child has always been very close to target,
		#  for example 0.030, 0.042 or 0.048 away from bounding rhomb. Observed at levels 1 and 2 of search. For now,
		#  I'm changing the value here back to theoretical, but I'd like to figure out why my brute force measurement
		#  was wrong.
		# More apparent exceptions: 0.2504585925389473, 0.2563185433459001, 0.2559212731069851, 0.2060401723750226,
		# 0.25458511670379114. 0.27080803857963665, 0.27049171239589354,
		# The following values are apparently caused by missing level 6 chunks below a level 7 chunk; values were
		# reported as the player traveled through the level 7 chunk, quite obviously inside it the entire time. So,
		# at least some of the problem is caused by this. 0 . 3 3 9 2 4 3 1 6 5 2 6 0 7 2 2 0 7, 0 . 3 3 9 2 4 5 7 3 6 5 9 9 6 4 8 1
		# 0 . 3 3 9 2 4 8 3 0 7 9 3 8 5 7 3 9 7,  0 . 3 3 9 4 5 2 7 2 9 3 8 3 1 9 0 5, 0 . 3 3 9 4 5 5 3 0 0 7 2 2 1 1 6 4,  0 . 3 3 9 4 9 0 6 5 6 6 3 2 3 4 8 8, 0 . 3 3 9 4 9 5 7 9 9 3 1 0 2 0 0 8,
		# 0 . 3 3 9 5 0 5 4 4 1 8 3 1 1 7 3 3 7, 0 . 3 3 9 5 0 8 0 1 3 1 7 0 0 9 9 4, 0 . 3 3 9 6 9 5 7 2 0 9 1 1 6 9 6 8 6, 0 . 3 3 9 6 9 8 2 9 2 2 5 0 6 2 2 8 7, 0 . 3 3 9 7 0 0 8 6 3 5 8 9 5 4 8 9,
		# 0 . 3 3 9 9 7 7 1 6 9 6 5 3 0 1 1 8 3, 0 . 3 3 9 9 7 9 7 3 9 0 8 6 9 4 0 5 7, 0 . 3 4 0 0 3 1 7 7 0 1 2 3 9 9 9 6 5
		# Using a more cautious, less principled value for now.....
		# BIG, NEWS, OBVIOUS IN HINDSIGHT: Thanks to brainstorming on Discord, I have realized that the value I'm using
		#   should simply depend on level. Picture a really high-level chunk being subdivided repeatedly. First it
		#   loses up to 14.2% around the edges (as far as our absolute certainty goes), as its sub-chunks are filled in.
		#   Then, it loses up to 14.2% of a sub-chunk edge length (which is a factor of phi^3 smaller). Then it loses
		#   14.2% of a sub-sub-chunk edge length. These repeated sums, for a level N chunk, give a territory loss of
		#   c * phi^3 * (phi^(3N) - 1) / (phi^3 - 1). (Gain should be the same) This is still a simplified worst-case,
		#   but it seems like it would be hard to come up with a better model. Perhaps I could experimentally measure
		#   one more level for a better starting point.
		#scale_formula = self.network.phipow(2) * (self.network.phipow(3 * self.level) - 1) / 2
		scale_formula = self.network.phipow(2) * (self.network.phipow(3 * self.level) - 1) / (2*self.network.phipow(3 * self.level))
		return self.rhomb_contains_point(point) > 0.141996 * scale_formula #0.1859  # 0.271#0.19793839129906832

	def might_contain_point(self, point, block_level=0):
		"""
		Returns true if the point is inside the rhombohedral boundary, but also returns true if the point falls close
		enough to the chunk that some block belonging to this chunk might jut out of the chunk's rhombohedral boundary
		and turn out to contain the point.
		:param point: A 3D point, given in worldplane coordinates.
		:param block_level: At and below this level, no safety margin is used since blocks genuinely have rhombohedral boundaries.
		:return: Boolean.
		"""
		if self.level <= block_level:
			return self.rhomb_contains_point(point) > 0
		# For now, just using the same quick test as safely_contains_point.
		# TODO safely_contains and might_contain ought to be coupled, to prevent me changing the value in one place and
		#  forgetting the other (which I just now did).
		scale_formula = self.network.phipow(2) * (self.network.phipow(3 * self.level) - 1) / (2*self.network.phipow(3 * self.level))
		return self.rhomb_contains_point(point) > -0.141996 * scale_formula#-0.1859  # 0.271#-0.19793839129906832#-0.14199511391282338

	def chunk_at_location(self, target, target_level=0, generate=False, verbose=False):
		"""
		Takes a 3D coordinate and returns the smallest list of already-generated chunks guaranteed to contain that coordinate.
		The search proceeds from the present chunk, so it should be treated as a best-guess.
		:param target:
		The coordinates to search for.
		:param target_level:
		The level of chunk desired, with blocks being target_level 0. If chunks of the desired level have not yet been
		generated, by default this will return the closest available level.
		:param generate:
		Set generate=True to force generation of the desired level of chunks. Note, this can either force generation
		down to target_level, or up to target_level, or some combination; for example we can request a chunk of level 10
		(about the scale of Earth's moon), and place it a cauple hundred million blocks away from us (about the distance
		to the moon), and this forces the generation of a highest-level chunk of approximately level 14, subdivided just
		enough to produce the requested level 10 chunk.
		:return: Returns a list of Chunk objects. If these are block-level or below, they are just temporary objects
		for sake of convenience; they know which chunks are their parent but those chunks don't acknowledge them as
		children. If generate=False, the list will be empty if nothing appropriate exists.
		"""
		# TODO Maybe for logging purposes, verbose should be able to be a string, stating the reason for verbosity.
		#  The string would then be prepended to each line.
		if verbose: print("Search invoked at level " + str(self.level) + ".\nTarget level " + str(target_level) + ".")
		# TODO When generate=False and target_level is below what's been generated, should dummy chunks be returned
		#  like in the block case? Or maybe target_level=1 should be the default and the dummy chunks system should
		#  be replaced with an extra function for finding block coordinates within a chunk.
		# To avoid moving up and down and up and down the tree of chunks, we must first move up and then move down.
		# Recursive calls of chunk_at_location will move up only.
		if self.safely_contains_point(target):
			if verbose: print("Level " + str(self.level) + " safely contains target.")
			if self.level == target_level:
				return [self]
			if self.level > target_level:
				# We're far up enough; move downwards.
				return self._child_chunk_search(target, target_level, generate, verbose)
			if self.level < target_level:
				if self.parent != None:
					return self.parent.chunk_at_location(target, target_level, generate, verbose)
				else:
					if generate:
						return self.get_parent().chunk_at_location(target, target_level, generate, verbose)
					else:
						# We're the highest-level chunk available which contains the point, although a higher level
						# was requested for some strange reason. This is odd enough that it should be logged, but,
						# the right behavior is to return ourselves.
						print("WARNING: Call to chunk_at_location probably missing argument 'generate=True'; "
							  + "a chunk of higher level than available was requested.")
						return [self]
		else:
			if self.parent is not None:
				return self.parent.chunk_at_location(target, target_level, generate, verbose)
			else:
				if generate:
					print("Top-level chunk is " + str(self.level) + "; target not safely inside."
						  + "Target distance: " + str(self.rhomb_contains_point(target)) + ". Generating new parent.")
					return self.get_parent().chunk_at_location(target, target_level, generate, verbose)
				else:
					if self.might_contain_point(target):
						if target_level < self.level:
							# We don't know for sure the point lies within this chunk, but we can check anyway.
							return self._child_chunk_search(target, target_level, generate, verbose)
						else:
							# The point could be here, but just returning [self] wouldn't return a list guaranteed to
							# contain the target, so we have to give an empty return.
							print("Search returning because we can't generate high enough chunk levels for certainty.")
							return []
					else:
						# The point lies outside the generated chunk tree.
						print("Search returning; target lies outside existing tree and generate=False.")
						return []

	def _creeping_search(self, target, target_level, generate, verbose=False):
		#TODO This *seems* like it should be a decent search strategy, but was only really tested when the
		# chunk network was a bit broken.
		creeper = self
		generate = True
		while creeper.level > target_level or creeper.rhomb_contains_point(target) < -1e-15:
			neighbors = [x for x in creeper.get_neighbors(generate).flatten() if x is not None]
			neighbor_scores = np.array([x.rhomb_contains_point(target) for x in neighbors])
			print("creeping: Neighbor scores:")
			for s in neighbor_scores:
				print("creeping: " + str(s))
			# If creeper is a local maximum, current chunk is a good guess. Descend a level.
			if neighbors[neighbor_scores.argmax()] is creeper:
				print("creeping: Own score is best, descending to level " + str(creeper.level - 1))
				# Generate is currently true
				children = creeper.get_children()
				# Should choose the middle, or closest to target, but for now randomize amongst non-edge
				inner_children = [creeper.children[i] for i in range(len(creeper.children))
								  if len(np.nonzero(creeper.blocks_neighbor[i])[0]) == 6]
				creeper = random.choice(inner_children)
			else:
				# Move to neighbor nearest our target
				print("creeping: Creeping along level " + str(creeper.level))
				creeper = neighbors[neighbor_scores.argmax()]
		# If we ever got out of the while loop, we should be at a real solution
		return creeper

	def _child_chunk_search(self, target, target_level, generate, verbose=False):
		"""
		This function is meant to be called from within chunk_at_location in order to do the downward half of the
		recursive search. The functionality is the same as chunk_at_location except that this function assumes the
		target lies within this chunk.
		:param target: The coordinates to search for.
		:param target_level: The level of chunk desired, with blocks being target_level 0. If chunks of the desired
		level have not yet been generated, by default this will return the closest available level.
		:param generate: Set generate=True to force generation of the desired level of chunks. Note, this can either
		force generation down to target_level, or up to target_level, or some combination; for example we can request a
		chunk of level 10 (about the scale of Earth's moon), and place it a cauple hundred million blocks away from us
		(about the distance to the moon), and this forces the generation of a highest-level chunk of approximately level
		14, subdivided just enough to produce the requested level 10 chunk.
		:return: Returns a list of Chunk objects. If these are block-level or below, they are just temporary objects
		for sake of convenience; they know which chunks are their parent but those chunks don't acknowledge them as
		children. If generate=False, the list will be empty if nothing appropriate exists.
		"""
		if verbose: print("Search descended to level " + str(self.level))
		if self.level == target_level:
			# We assume the function wouldn't have been called if the point weren't nearby, so, this chunk is the best bet.
			if verbose: print(
				"This is the target level; returning self. Containment: " + str(self.rhomb_contains_point(target)))
			return [self]
		if self.level < target_level:
			# This should be unreachable.
			raise Exception("_child_chunk_search has descended lower than its target level of " + str(target_level)
							+ ".\nCurrent chunk level: " + str(self.level) + "."
							+ "\nWas _child_chunk_search accidentally called instead of chunk_at_location?")
		child_list = []
		if generate or self.all_children_generated:
			child_list = self.get_children()
		else:
			child_list = self.get_existing_children()
			if child_list is None or len(child_list) == 0:
				# We can't eliminate the possibility that the target is here, so we return self.
				if verbose: print(
					"No available children; returning self. Containment: " + str(self.rhomb_contains_point(target)))
				return [self]
		priority_list = [child.rhomb_contains_point(target) for child in child_list]
		sorted_indices = list(range(len(priority_list)))
		sorted_indices.sort(key=lambda x: priority_list[x], reverse=True)
		if child_list[sorted_indices[0]].safely_contains_point(target):
			# No need to search more than one children, this one contains the point.
			if verbose: print(
				"A child safely_contains; returning it. Containment: " + str(self.rhomb_contains_point(target)))
			return child_list[sorted_indices[0]]._child_chunk_search(target, target_level, generate)
		# Handle some special cases where no recursive search is needed
		if self.safely_contains_point(target):
			if verbose: print(
				"Level " + str(self.level) + " safely contains target; checking children. Containment: " + str(
					self.rhomb_contains_point(target)))
			if priority_list[sorted_indices[0]] < 0:
				# (One might think the condition here should be based on 'possibly contains', ie, if we safely
				# contain the target at least one child should possibly contain it; but actually 'safely contains'
				# provides a guarantee of the stronger condition above. This is as it should be; safely_contains
				# is extremely cautious.)
				if generate or self.all_children_generated:
					# We 'safely contain' the target but none of our children contain it??
					# raise Exception("Search terminated at level "+str(self.level)
					#				+": This chunk 'safely contains' target point but none of its children do.\n"
					#				+ "Target: "+str(target)
					#				+ "\nChunk offset: "+str(self.get_offset(level=0))
					#				+ "\nClosest child was "+str(-priority_list[sorted_indices[0]])+" away."
					#				+ "\nChild offset: "+str(child_list[sorted_indices[0]].get_offset(level=0)))
					print("Search terminated at level " + str(self.level)
						  + ": This chunk 'safely contains' target point but none of its children do.\n"
						  + "Target: " + str(target)
						  + "\nChunk offset: " + str(self.get_offset(level=0))
						  + "\nClosest child was " + str(-priority_list[sorted_indices[0]]) + " away."
						  + "\nChild offset: " + str(child_list[sorted_indices[0]].get_offset(level=0)))
					print("Checking neighbors of closest child...")
					# TODO This should be done as a loop through the priority list
					closest_child_neighbors = list(child_list[sorted_indices[0]].neighbors.flatten())
					closest_child_neighbors = [x for x in closest_child_neighbors if x is not None
											   and x is not child_list[sorted_indices[0]]]
					print("Found " + str(len(closest_child_neighbors)) + " neighbors.")
					cousins = [x for x in closest_child_neighbors if x.parent is not self]
					print("How many are new? " + str(len(cousins)))
					for c in closest_child_neighbors:
						print("Containment: " + str(c.rhomb_contains_point(target)))
					# TODO Remove this exception, it's just for debugging
					raise Exception("Abandoning attempt before creeping search.", self)
					# Try creeping search
					print("Trying creeping search")
					creeping_result = self._creeping_search(target, target_level, generate, verbose=True)
					return [creeping_result]
					return [self]
				else:
					# Some child must contain the point, but it apparently hasn't been generated yet; this chunk is the
					# best to return (assuming I even understand the use cases at all)
					if verbose: print("Correct child not generated; returning self. Containment: " + str(
						self.rhomb_contains_point(target)))
					return [self]
		else:
			# Target not within "safely_contains" margin; may actually belong to a neighbor.
			# However, search process reached this chunk, so this chunk is the guess nearest the point.
			if generate or self.all_children_generated:
				if not child_list[sorted_indices[0]].might_contain_point(target):
					# No point looking further.
					if verbose: print("Closest child: "+str(child_list[sorted_indices[0]].rhomb_contains_point(target)))
					if verbose: print("No child contains target; returning []. Containment: " + str(
						self.rhomb_contains_point(target)))
					return []
		# OK, no one child safely contains the point, and we weren't able to return [self] or [] based on a quick check.
		# So we need to return a list of all children which might contain it, combining output from multiple recursive
		# calls. We still may return [self] in the generate=False case, where we can't be sure our list is complete.
		if generate or self.all_children_generated:
			results = []
			for child_i in sorted_indices:
				if not child_list[child_i].might_contain_point(target):
					# Since children are ordered by distance to target, and that's all that's used in might_contain_point,
					# we know no further children might contain the target.
					# No need to return [self] if 'results' is empty; we then know this chunk doesn't contain the point.
					if verbose: print("No one child confirmed; returning list of " + str(len(results))
									  + " possible children. Containment: " + str(self.rhomb_contains_point(target)))
					break
				child_search_results = child_list[child_i]._child_chunk_search(target, target_level, generate, verbose)
				# If any one search returns something which definitely contains the target, we need to simply
				# return that.
				# TODO Write a test that we always manage to return a list of length one when we find the target inside
				#  some chunk.
				if len(child_search_results) == 1:
					# We only need to check when the length is 1, since the recursive call would return just one result
					# if that result actually contained the point.
					if child_search_results[0].safely_contains_point(target):
						if verbose: print(
							"Encountered child safely containing point; returning it. Containment: " + str(
								self.rhomb_contains_point(target)))
						return child_search_results
				results += child_search_results
			if len(results) == 0 and self.safely_contains_point(target):
				# raise Exception("Chunk at level "+str(self.level)+"'safely contains point', yet recursive search turned up empty."
				#				+"\nContainment: "+str(self.rhomb_contains_point(target))
				#				+"\nClosest child: "+str(priority_list[sorted_indices[0]]))
				print("\nChunk at level " + str(
					self.level) + " 'safely contains point', yet recursive search turned up empty."
					  + "\nContainment: " + str(self.rhomb_contains_point(target))
					  + "\nClosest child: " + str(priority_list[sorted_indices[0]]))
				print("Checking neighbors of closest child...")
				# TODO This should be done as a loop through the priority list
				closest_child_neighbors = list(child_list[sorted_indices[0]].neighbors.flatten())
				closest_child_neighbors = [x for x in closest_child_neighbors if x is not None
											   and x is not child_list[sorted_indices[0]]]
				print("Found "+str(len(closest_child_neighbors))+" neighbors.")
				cousins = [x for x in closest_child_neighbors if x.parent is not self]
				print("How many are new? "+str(len(cousins)))
				for c in closest_child_neighbors:
					print("Containment: "+str(c.rhomb_contains_point(target)))
				# TODO Make below an actual test
				#print("Let's see if the chunk contains its children.")
				#for child_i in sorted_indices:
				#    print(self.rhomb_contains_point(
				#        self.network.custom_pow(self.network.deflation_face_axes,self.level-1)
				#            .dot((self.children[child_i].get_offset(self.level-1) + (np.array(self.blocks[child_i])%1)))
				#            .dot(self.network.worldplane.T)))
				# Try creeping search
				# TODO Remove this exception, it's just for debugging
				raise Exception("Abandoning attempt before creeping search.", self)
				print("Trying creeping search")
				creeping_result = self._creeping_search(target, target_level, generate, verbose=True)
				return [creeping_result]
				return [self]

			return results
		else:
			# Now we need to check if any one child definitely contains the point. If not, the target could be in
			# a non-generated child, or could be in a neighboring chunk. So, this specific case is likely to cause
			# a lot of fruitless searching.
			# TODO This could be abbreviated by generating and returning 'temporary' chunks.
			# Note: at the moment, I have never seen this warning get printed, which is actually a bit odd.
			print(
				"Warning: Potentially expensive search is occurring at edge of generated grid. If this message"
				+ " is printed many times, consider using generate=True in the code responsible for the warning.")
			for child_i in sorted_indices:
				if not child_list[child_i].might_contain_point(target):
					# We've gone far enough in the list with no results.
					return [self]
				child_search_results = child_list[child_i]._child_chunk_search(target, target_level, generate)
				# We only care if one of the results definitely contains the target.
				# We only need to check when the length is 1, since the recursive call would return just one result
				# if that result actually contained the point.
				if len(child_search_results) == 1:
					# TODO In some cases we call safely_contains_point or a related function 3 times per chunk
					#  (before the recursive search call, during it, and after it returns). Do one call and just
					#  pass around the resulting information?
					if child_search_results[0].safely_contains_point(target):
						return child_search_results
			# If we didn't return during the loop, there are no children definitely containing the target.
			# We don't want to return a list of all children that might contain the target, because it might
			# be incomplete. We shouldn't return an empty list, because the search process reached this far so
			# the present chunk is a possible location of target (it might even be a sure location).
			return [self]

	def increment_search(self, target):
		"""A debugging-oriented search/generation algorithm, for when the chunk network is broken."""
		if self.level == 0 and self.rhomb_contains_point(target) >= 0:
			print(str(self)+ " is a block containing the player! Perfect.")
			return [self]
		if self.level == 0:
			print("Block didn't contain player")
			return [self.get_parent()]
		if self.level == 1 and self.safely_contains_point(target):
			print(str(self)+ " is level 1 and safely contains player, which should be sufficient.")
			self.get_children()
			return [self]
		print(str(self)+" at level "+str(self.level)+ " is not immediately sufficient. Checking.")
		actual_children = [chunk for chunk in self.get_children() if chunk is not None]
		# all_possible_children = self.network.generate_children(self.template_index, self.offset, self.level,False)# True)
		# possible_child_chunks = [Chunk(self.network, child[0], child[1], self.level - 1, True) for child in all_possible_children]
		# def cleanup(possible_child_chunks = possible_child_chunks):
		#     for chunk in possible_child_chunks:
		#         del chunk
		#     del possible_child_chunks
		safely_contains_check = [c.safely_contains_point(target) for c in actual_children]#possible_child_chunks]
		might_contain_check = [c.might_contain_point(target) for c in actual_children]#possible_child_chunks]
		if np.any(safely_contains_check):
			# We have the safely_contains guarantee, and need no upwards search.
			for a_child in actual_children:
				if a_child.safely_contains_point(target):
					#cleanup()
					return [a_child]
			print ("Found player in outside hit, leaving for later.")
			# Hmm ok, it was an outside hit. May need upwards search; deal with this after.
		parent_stack = [self]
		while parent_stack[-1].parent is not None:
			parent_stack.append(parent_stack[-1].parent)
		parent_safely_contains_check = [c.safely_contains_point(target) for c in parent_stack]
		if not np.any(parent_safely_contains_check):
			print("Highest parent does not safely contain target;")
			print('player dist into parent: '+str(parent_stack[-1].rhomb_contains_point(target)))
			scale_formula = self.network.phipow(2) * (self.network.phipow(3 * self.level) - 1) / (2*self.network.phipow(3 * self.level))
			print(' range for safe containment: '+str(0.141996 * scale_formula))
			parent_stack.append(parent_stack[-1].get_parent())
			# We added a new chunk, so that counts as an increment.
			print("Added new parent.")
			#cleanup()
			return [parent_stack[-1]]
		# if np.any(safely_contains_check):
		#     print("Outside hit; attempting to join main tree.")
		#     # Due to the earlier check, we can assume the hit is not properly our own child.
		#     # This time we know there's some shared ancestor between self and the child's proper parent.
		#     # We know the shared ancestor is already instantiated, because the top of the tree safely_contains the
		#     # target, which means it safely_contains the outside hit.
		#     hits = np.nonzero(safely_contains_check)[0]
		#     if len(hits) > 1:
		#         print("Somehow got "+str(len(hits))+" children which safely contain target.")
		#     possible_child = possible_child_chunks[hits[0]]
		#     child_parent_stack = [possible_child]
		#     united = False
		#     # Because we're doing this with a merely possible child, we have to do it all in one go, not incrementally.
		#     # This is unfortunate, since there will be a lot of hits like this.
		#     parent_stack_templates = [p.template_index for p in parent_stack]
		#     # TODO Maybe totally skip this if the current chunk doesn't even possibly contain the target.
		#     matching_ancestor = None
		#     while len(child_parent_stack) <= len(parent_stack) and not united:
		#         child_parent_stack.append(child_parent_stack[-1].get_parent())
		#         new_parent = child_parent_stack[-1]
		#         if new_parent.template_index in parent_stack_templates:
		#             possible_matches = [parent_stack[template_match] for template_match in np.nonzero(np.array(parent_stack_templates) == new_parent.template_index)[0]]
		#             for possible_match in possible_matches:
		#                 if np.all(possible_match.offset == new_parent.offset):
		#                     # We've got a match.
		#                     united = True
		#                     matching_ancestor = possible_match
		#     if not united:
		#         print("Found a chunk at level "+str(self.level - 1)+" which safely contained target.\n"
		#               + "However, failed to find a shared parent with existing hierarchy.")
		#         cleanup()
		#         return []
		#     # We just need to locate the match in the existing hierarchy.
		#     child_parent_stack.reverse()
		#     child_parent_stack = child_parent_stack[:-1]
		#     print("Found a solid hit; evaluating a parent stack:")
		#     print(child_parent_stack)
		#     lowest_match = matching_ancestor
		#     match_count = 0
		#     for possible_chunk in child_parent_stack:
		#         sift_amongst = [chunk for chunk in lowest_match.get_children() if chunk is not None]
		#         sifted_template = [c.template_index == possible_chunk.template_index for c in sift_amongst]
		#         sifted_offset = [np.all(c.offset == possible_chunk.offset) for c in sift_amongst]
		#         if not np.any(sifted_template) or not np.any(sifted_offset):
		#             print("Unable to merge entire parent stack; returning lowest hit. Matched "+str(match_count)+".")
		#             cleanup()
		#             cleanup(child_parent_stack)
		#             return [lowest_match]
		#         lowest_match = sift_amongst[np.nonzero(np.array(sifted_template)*np.array(sifted_offset))[0][0]]
		#         match_count += 1
		#     print("Entire parent stack recreated. Returning the outside hit.")
		#     cleanup()
		#     cleanup(child_parent_stack)
		#     return [lowest_match]
		# The best we can do is return all children which might contain the target.
		if not np.any(might_contain_check):
			print("This chunk is far from the target; backing up.")
			# cleanup()
			return [parent_stack[-1]]
		if self.level <= 1:
			# A level 1 might-contain could be the best we can get, but it could also mean we need to back up, so,
			# unfortunately we can't just return self.
			# cleanup()
			return [self.parent]
		# It's ok to ignore outside hits now, since there's a safely containing parent. There might still be oddities,
		# but we don't have a safely_contains hit to use to dig into details.
		might_contains = [c for c in actual_children if c is not None and c.might_contain_point(target)]
		print("Returning "+str(len(might_contains))+" might-contains of level "+str(self.level-1))
		# cleanup()
		return might_contains


	def highlight_block(self):
		"""
		Draws an outline around a block.
		:return: None.
		"""

		self.network.block_highlight.show()
		self.network.block_highlight.clear()

		# TODO This is the sort of stuff I should have helper functions for
		pa_center = self.network.all_blocks[self.get_parent().template_index][0][
			self.get_parent().children.index(self)] + self.get_parent().get_offset()
		self.network.block_highlight.begin(Mesh.PRIMITIVE_LINES)
		self.network.block_highlight.set_color(Color(0,0,0))
		self.network.draw_block_wireframe(pa_center, self.network.block_highlight, 1)
		self.network.block_highlight.end()

		# # TODO This should make use of self.network.draw_block_wireframe.
		# template_center = self.network.chunk_center_lookup(self.template_index)
		# # We use get_offset's default level (zero) so we don't need scale multipliers.
		# block = self.get_offset() + 0.5 - (template_center - np.floor(template_center))
		# block = np.array(np.round(block * 2), dtype=np.float) / 2.0
		# # print("hilite "+str(block))
		# face_origin = np.floor(block).dot(self.network.worldplane.T)
		# face_tip = np.ceil(block).dot(self.network.worldplane.T)
		# dir1, dir2, dir3 = np.eye(6)[np.nonzero(np.ceil(block) - np.floor(block))[0]].dot(
		# 	self.network.worldplane.T)
		# face_origin = Vector3(face_origin[0], face_origin[1], face_origin[2])
		# face_tip = Vector3(face_tip[0], face_tip[1], face_tip[2])
		# dir1 = Vector3(dir1[0], dir1[1], dir1[2])
		# dir2 = Vector3(dir2[0], dir2[1], dir2[2])
		# dir3 = Vector3(dir3[0], dir3[1], dir3[2])
		# # dumb_highlight = MeshInstance.new()
		# # dumb_highlight.mesh = SphereMesh()
		# # dumb_highlight.translation = face_origin
		# # self.network.add_child(dumb_highlight)
		# # dh_pos = dumb_highlight.global_transform.origin
		# # dh_pos = np.array([dh_pos.x, dh_pos.y, dh_pos.z])
		# # player_pos = self.network.get_node("../../Player").transform.origin
		# # player_pos = np.array([player_pos.x, player_pos.y, player_pos.z])
		# # print(dh_pos - player_pos)
		# self.network.block_highlight.begin(Mesh.PRIMITIVE_LINES)
		# self.network.block_highlight.add_vertex(face_origin)
		# self.network.block_highlight.add_vertex(face_origin + dir1)
		# self.network.block_highlight.add_vertex(face_origin)
		# self.network.block_highlight.add_vertex(face_origin + dir2)
		# self.network.block_highlight.add_vertex(face_origin)
		# self.network.block_highlight.add_vertex(face_origin + dir3)
		# self.network.block_highlight.add_vertex(face_origin)
		# self.network.block_highlight.end()

	def fill(self):
		"""
		Fill the block and cause world mesh to update.
		:return:
		"""
		self.get_parent().block_values[self.index_in_parent] = 1
		self.get_parent().draw_mesh()

	def draw_mesh(self, drawp=lambda x: True):
		"""
		Creates a mesh consisting of the chunk's children (ie, blocks, if the chunk is level 1); then adds that mesh
		as a child of self.network so that it will be drawn.
		:param drawp: Optional function which can take a block and returns true or false. If false is returned, we
		won't draw that block.
		:return: none
		"""
		starttime = time.perf_counter()

		self.drawn = True
		# TODO Generate mesh in separate thread(s), like the pure-gdscript voxel game demo does.
		# st = SurfaceTool()
		if self.level >= 1:
			multiplier = self.network.phi_powers[(self.level - 1) * 3]
		if self.level < 1:
			multiplier = 1.0 / self.network.phi_powers[-((self.level - 1) * 3)]
		# st.begin(Mesh.PRIMITIVE_TRIANGLES)
		# st.add_color(Color(r.random(), r.random(), r.random()))

		vertices = PoolVector3Array()
		indices = PoolIntArray()
		normals = PoolVector3Array()

		body = StaticBody.new()
		collider = CollisionShape.new()
		body.add_child(collider)
		# TODO If I can write a custom collider shape for the Ammann rhombohedra, there may be ways to make it fast.
		collider.shape = ConcavePolygonShape()
		collider_face_array = PoolVector3Array()

		preliminaries = time.perf_counter()

		# The block corner indices are added in a predictable order, so we can construct our index array all at once.
		# The pattern for one block is stored in the Chunk_Network as rhomb_indices. Here's how it looks.
		# rhomb_indices = np.array([0, 2, 7, 0, 7, 3, 0, 3, 5, 0, 5, 4, 0, 4, 6, 0, 6, 2, 1, 4, 5, 1, 6, 4, 1, 2, 6, 1, 7, 2, 1, 3, 7, 1, 5, 3])
		# Now we just need to add the offset of 8 for each new block.
		to_draw = np.array(
			[self.block_values[block_i] > 0 and drawp(self.blocks[block_i]) for block_i in range(len(self.blocks))])
		blocks_to_draw = [self.blocks[i] + self.offset for i in range(len(to_draw)) if to_draw[i]]
		# Check for exposed faces
		# print(sum(self.blocks_neighbor[block_i]))
		# if sum(self.blocks_neighbor[block_i]) >= 6:
		# 	# Six neighbors lie inside this chunk
		# 	if np.nonzero(self.block_values[np.nonzero(self.blocks_neighbor[block_i])[0]])[0].shape[0] == 6:
		# 		# Skip this block
		# 		print("Skipping a block yay!")
		# 		continue
		build_draw_list = time.perf_counter()

		num_to_draw = sum(to_draw)

		if num_to_draw == 0:
			collider.free()
			body.free()
			return

		index_data = np.tile(self.network.rhomb_indices, num_to_draw) \
					 + 8 * np.repeat(np.arange(num_to_draw), len(self.network.rhomb_indices))
		# Careful now!
		indices.resize(36 * num_to_draw)
		with indices.raw_access() as indices_dump:
			for i in range(36 * num_to_draw):
				indices_dump[i] = index_data[i]

		index_precalc = time.perf_counter()

		block_origins = np.floor(blocks_to_draw).dot(self.network.worldplane.T) * multiplier
		block_axes = ((np.array([np.eye(6)] * len(blocks_to_draw))[np.ceil(blocks_to_draw)
																   - np.floor(blocks_to_draw) != 0]).dot(
			self.network.worldplane.T) * multiplier
					  ).reshape((len(blocks_to_draw), 3, 3))
		# right hand rule
		block_axes_flipped = block_axes[:, [1, 0, 2], :]
		block_axes = np.where(
			np.repeat(np.diag(np.cross(block_axes[:, 0], block_axes[:, 1]).dot(block_axes[:, 2].T)) < 0, 9).reshape(-1,
																													3,
																													3),
			block_axes_flipped, block_axes)
		corner1 = block_origins
		corner2 = block_origins + np.sum(block_axes, axis=1)
		corner3 = block_origins + block_axes[:, 0]
		corner4 = block_origins + block_axes[:, 1]
		corner5 = block_origins + block_axes[:, 2]
		corner6 = corner2 - block_axes[:, 0]
		corner7 = corner2 - block_axes[:, 1]
		corner8 = corner2 - block_axes[:, 2]

		center = (block_origins + np.sum(block_axes, axis=1) / 2).repeat(8, axis=0)

		vertices_data = np.array([corner1, corner2, corner3, corner4,
								  corner5, corner6, corner7, corner8]).transpose((1, 0, 2)).reshape((-1, 3))

		vertices.resize(8 * num_to_draw)
		with vertices.raw_access() as vertices_dump:
			for i in range(8 * num_to_draw):
				vertices_dump[i] = Vector3(vertices_data[i][0], vertices_data[i][1], vertices_data[i][2])

		normal_data = (vertices_data - center) / np.linalg.norm(vertices_data - center, axis=1).repeat(3).reshape(
			(-1, 3))
		normals.resize(8 * num_to_draw)
		with normals.raw_access() as normals_dump:
			for i in range(8 * num_to_draw):
				normals[i] = Vector3(normal_data[i][0], normal_data[i][1], normal_data[i][2])

		vertex_precalc = time.perf_counter()

		# Now that we've got the vertices, let's try and calculate the colliders in one step too.
		if len(vertices) > 0:
			# Converting the PoolVector3Array to a numpy array simply flattens, for 3x the length
			collider_data = np.array(vertices)[index_data]
			# Careful now!
			collider_face_array.resize(36 * 3 * num_to_draw)
			with collider_face_array.raw_access() as collider_dump:
				for i in range(36 * num_to_draw):
					collider_dump[i] = collider_data[i]
		collision_precalc = time.perf_counter()
		# Finalize mesh for the chunk

		new_mesh = ArrayMesh()
		arrays = Array()
		arrays.resize(ArrayMesh.ARRAY_MAX)
		arrays[ArrayMesh.ARRAY_VERTEX] = vertices
		arrays[ArrayMesh.ARRAY_INDEX] = indices
		arrays[ArrayMesh.ARRAY_NORMAL] = normals
		arrays[ArrayMesh.ARRAY_COLOR] = PoolColorArray(
			Array([Color(r.random(), r.random(), r.random())] * len(vertices)))
		new_mesh.add_surface_from_arrays(ArrayMesh.PRIMITIVE_TRIANGLES, arrays)
		new_mi = MeshInstance.new()
		new_mi.mesh = new_mesh
		new_mesh.surface_set_material(new_mesh.get_surface_count() - 1, COLOR)


		# The MI needs to be able to tell us about collisions

		new_mi.set_meta("originating_chunk", GDString(str(id(self))))
		print(new_mi.get_meta("originating_chunk"))

		self.network.add_child(new_mi)
		new_mi.show()

		add_surface = time.perf_counter()

		# Finalize collision shape for the chunk
		collider.shape.set_faces(collider_face_array)
		body.collision_layer = 0xFFFFF
		body.collision_mask = 0xFFFFF
		new_mi.add_child(body)

		add_collider = time.perf_counter()

		# If there was an old mesh, delete it
		if self.mesh is not None:
			self.network.remove_child(self.mesh)
			self.mesh.free()
		self.mesh = new_mi
		final_time = time.perf_counter()
	# print("\nPreliminaries:     "+str(preliminaries - starttime))
	# print("Build draw list:   "+str(build_draw_list - preliminaries))
	# print("Index building:    "+str(index_precalc - build_draw_list))
	# print("Vertex building:   "+ str(vertex_precalc - index_precalc))
	# print("Collision precalc: "+str(collision_precalc - vertex_precalc))
	# print("Add surface:       "+str(add_surface - collision_precalc))
	# print("Add Collider:      "+str(add_collider - add_surface))
	# print("Final time:        "+ str(final_time - add_collider))

class GoldenField(numpy.lib.mixins.NDArrayOperatorsMixin):

	phi = 1.61803398874989484820458683

	golden64 = np.dtype([('int', np.int64),('phi', np.int64), ('dmo', np.int64)])
	golden32 = np.dtype([('int', np.int32), ('phi', np.int32), ('dmo', np.int32)])

	def fib(self, n):
		return self._fib(n)[0]

	def _fib(self, n):
		if n == 0:
			return (0,1)
		else:
			a, b = self._fib(n//2)
			c = a * (b * 2 - a)
			d = a * a + b * b
			if n % 2 == 0:
				return (c, d)
			else:
				return (d, c + d)

	def __init__(self, values):
		"""Format is [a,b,c] representing (a + bφ)/(c+1).
		Note the one-off denominator; so 1 is [1,0,0]."""
		if type(values) is list:
			values = np.array(values)
		if values.dtype in [self.golden64, self.golden32]:
			self.ndarray = values
		elif values.shape[-1] == 3 and values.dtype.kind in ['u', 'i']:
			self.ndarray = np.zeros(values[...,0].shape, dtype=self.golden64)
			self.ndarray['int'] = values[...,0]
			self.ndarray['phi'] = values[...,1]
			self.ndarray['dmo'] = values[...,2]
		else:
			# I'd like to accept other shapes, but that could lead to misunderstandings.
			raise ValueError("Not a valid golden field array; last axis must be of size 3.")

	def __repr__(self):
		if self.ndarray.shape == ():
			# Zero dimensional arrays must be printed differently
			return f"{self.__class__.__name__}({self.ndarray})"
		else:
			return f"{self.__class__.__name__}({list(self.ndarray)})"

	def __array__(self, dtype=None):
		return (self.ndarray['int'] + self.phi * self.ndarray['phi'])/(self.ndarray['dmo']+1)

	def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
		if method == '__call__':
			# Check if all integer
			all_integer = True
			for input in inputs:
				if not isinstance(input, numbers.Integral):
					if isinstance(input, np.ndarray):
						if not (input.dtype.kind in ['u', 'i']):
							all_integer = False
					elif isinstance(input, self.__class__):
						pass
					else:
						all_integer = False
			if not all_integer:
				# If we're not dealing with integers, there's no point in
				# staying a GoldenField.
				#TODO Could support fractions.Fraction/numbers.Rational, tho I don't know when it's ever used.
				return ufunc(np.array(self), *inputs, **kwargs)

			if ufunc == np.add:
				# (a + bφ)/c + (d + eφ)/f = ( (fa+cd) + (fb+ce)φ )/cf
				returnval = np.zeros(self.ndarray.shape, dtype=self.golden64)
				returnval['dmo'] = 1
				for input in inputs:
					old_rv = returnval.copy()
					if isinstance(input, self.__class__):
						returnval['int'] = old_rv['int']*(input.ndarray['dmo']+1) + input.ndarray['int']*(old_rv['dmo']+1)
						returnval['phi'] = old_rv['phi']*(input.ndarray['dmo']+1) + input.ndarray['phi']*(old_rv['dmo']+1)
						returnval['dmo'] = (old_rv['dmo']+1)*(input.ndarray['dmo']+1) - 1
					else:
						# Just add to the integer part
						returnval['int'] = returnval['int'] + input * (returnval['dmo'] + 1)
				return self.__class__(returnval).simplify()
			elif ufunc == np.subtract:
				# (a + bφ)/c - (d + eφ)/f = ( (fa-cd) + (fb-ce)φ )/cf

				returnval = np.zeros(self.ndarray.shape, dtype=self.golden64)
				# First argument is add, not subtract
				if isinstance(inputs[0], self.__class__):
					returnval = inputs[0].ndarray.copy()
				elif isinstance(inputs[0], np.ndarray):
					returnval['int'] = inputs[0]
				elif isinstance(inputs[0], numbers.Integral):
					returnval['int'] = inputs[0]
				else:
					return NotImplemented
				for input in inputs[1:]:
					old_rv = returnval.copy()
					if isinstance(input, self.__class__):
						returnval['int'] = old_rv['int']*(input.ndarray['dmo']+1) - input.ndarray['int']*(old_rv['dmo']+1)
						returnval['phi'] = old_rv['phi']*(input.ndarray['dmo']+1) - input.ndarray['phi']*(old_rv['dmo']+1)
						returnval['dmo'] = (old_rv['dmo']+1)*(input.ndarray['dmo']+1)-1
					else:
						# Just add to the integer part
						returnval['int'] = returnval['int'] - input * (returnval['dmo'] + 1)
				return self.__class__(returnval).simplify()
			elif ufunc == np.multiply:
				# (a + bφ)/c * (d + eφ)/f = ( (ad + be) + (ae + bd + be)φ)/cf

				# Multiplicative identity is [1,0,1]
				returnval = np.zeros(self.ndarray.shape, dtype=self.golden64)
				returnval['int'] = 1
				for input in inputs:
					old_rv = returnval.copy()
					if isinstance(input, self.__class__):
						returnval['int'] = old_rv['int']*input.ndarray['int'] + old_rv['phi']*input.ndarray['phi']
						returnval['phi'] = old_rv['int']*input.ndarray['phi'] + old_rv['phi']*(input.ndarray['int']+input.ndarray['phi'])
						returnval['dmo'] = (old_rv['dmo']+1)*(input.ndarray['dmo']+1)-1
					elif isinstance(input, np.ndarray):
						# Multiply both parts by the array
						returnval['int'] = returnval['int'] * input
						returnval['phi'] = returnval['phi'] * input
					elif isinstance(input, numbers.Integral):
						returnval['int'] = returnval['int'] * input
						returnval['phi'] = returnval['phi'] * input
					else:
						return NotImplemented
				return self.__class__(returnval).simplify()
			elif ufunc == np.true_divide or ufunc == np.floor_divide:
				returnval = np.zeros(self.ndarray.shape, dtype=self.golden64)
				# First argument is multiply, not divide
				if isinstance(inputs[0], self.__class__):
					returnval = inputs[0].ndarray.copy()
				elif isinstance(inputs[0], np.ndarray):
					returnval['int'] = inputs[0]
				elif isinstance(inputs[0], numbers.Integral):
					returnval['int'] = inputs[0]
				else:
					return NotImplemented
				# (a + bφ)/c / (d + eφ)/f = ( f(ad + ae - be) + f(-ae + bd)φ ) / c(dd + de - ee)
				for input in inputs[1:]:
					old_rv = returnval.copy()
					if isinstance(input, self.__class__):
						returnval['int'] = (input.ndarray['dmo']+1)*(old_rv['int']*(input.ndarray['int'] + input.ndarray['phi']) - old_rv['phi']*input.ndarray['phi'])
						returnval['phi'] = (input.ndarray['dmo']+1)*(-old_rv['int']*input.ndarray['phi'] + old_rv['phi']*input.ndarray['int'])
						returnval['dmo'] = (old_rv['dmo']+1)*(input.ndarray['int']*(input.ndarray['int'] + input.ndarray['phi']) - input.ndarray['phi']*input.ndarray['phi']) - 1
					elif isinstance(input, np.ndarray):
						returnval['dmo'] = (returnval['dmo']+1) * input - 1
					elif isinstance(input, numbers.Integral):
						returnval['dmo'] = (returnval['dmo']+1) * input - 1
					else:
						return NotImplemented
				return self.__class__(returnval).simplify()
			elif ufunc == np.power:
				# Powers of phi can be taken using the fibonacci sequence.
				# pow(φ, n) = F(n-1) + F(n)φ
				# pow((a + bφ)/c, n) = ( Σ(i..0..n)(a^i * b^(n-i) * F(n-i+1) * (i C n)) + Σ(i..0..n)(a^i * b^(n-i) * F(n-i))φ * (i C n)) / c^n
				# Currently support arrays as the base but only plain integers as the exporent.
				base = np.zeros_like(self.ndarray)
				returnval = np.zeros_like(self.ndarray)
				if isinstance(inputs[0], self.__class__):
					base = inputs[0].ndarray.copy()
				elif isinstance(inputs[0],np.ndarray):
					base['int'] = inputs[0]
				else:
					# A plain number should be broadcast to an array but I don't know how to handle that yet.
					return NotImplemented
				if isinstance(inputs[1], self.__class__):
					# Exponents including phi don't stay in the golden field.
					# We could check whether inputs[1] is actually all rationals, but purely based on type, this
					# case shouldn't be implemented.
					#TODO Numpy isn't converting us automatically to a plain number like I expected.
					return NotImplemented
				elif isinstance(inputs[1], np.ndarray) and inputs[1].dtype.kind == 'i':
					# We should be able to handle this, but I haven't figured out a fast implementation yet and
					# I also don't have a use case.
					return NotImplemented
				elif isinstance(inputs[1], numbers.Integral):
					# This, we can handle.
					if inputs[1] == 0:
						# We could handle 0 directly, but we know what the value would be so that'd be silly.
						returnval = np.ones_like(base)
						returnval['phi'] = 0
					else:
						exponent = abs(inputs[1])
						i = np.arange(exponent+1)
						# We have to include the value of F(-1)
						fibs = [1,0,1]
						while len(fibs) <= exponent + 1:
							fibs.append(fibs[-1]+fibs[-2])
						fibs = np.array(fibs)
						returnval['int'] = np.sum(np.power(np.dstack([base['int']]*(exponent+1)),i)
												 *np.power(np.dstack([base['phi']]*(exponent+1)),exponent-i)
												   *np.flip(fibs[:-1]) * np.round(comb(exponent, i)),axis=-1)
						returnval['phi'] = np.sum(np.power(np.dstack([base['int']] * (exponent + 1)), i)
												   * np.power(np.dstack([base['phi']] * (exponent + 1)),
															  exponent - i)
												   * np.flip(fibs[1:] * np.round(comb(exponent, i))),axis=-1)
						returnval['dmo'] = pow((base['dmo']+1), exponent) - 1
						if inputs[1] < 0:
							returnval =  (1/self.__class__(returnval)).ndarray
					return self.__class__(returnval).simplify()
				else:
					return NotImplemented
			else:
				return NotImplemented
		else:
			return NotImplemented

	def __array_function__(self, func, types, args, kwargs):
		if func == np.ndarray.__getitem__:
			return self.ndarray.__getitem__(*args, **kwargs)
		return NotImplemented

	def __getitem__(self, key):
		return self.ndarray.__getitem__(key)

	@property
	def shape(self):
		return self.ndarray.shape

	def simplify(self):
		gcd = np.gcd.reduce([self.ndarray['int'], self.ndarray['phi'], (self.ndarray['dmo']+1)])
		self.ndarray['int'] = self.ndarray['int'] // gcd
		self.ndarray['phi'] = self.ndarray['phi'] // gcd
		self.ndarray['dmo'] = (self.ndarray['dmo']+1) // gcd - 1
		return self

test = GoldenField([[1,0,0],[0,1,0], [2, 2, 2]]); test2 = GoldenField([[0,0,0],[2,-1,0], [3, 0, 2]])
