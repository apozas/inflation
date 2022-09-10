import unittest
import numpy as np
import warnings
from causalinflation.quantum.general_tools import apply_source_permutation_coord_input, flatten
from causalinflation import InflationProblem, InflationSDP

class TestGeneratingMonomials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.simplefilter("ignore", category=DeprecationWarning)

    bilocalDAG = {"h1": ["v1", "v2"], "h2": ["v2", "v3"]}
    blilocal_names = ["v1", "v2", "v3"]
    inflation  = [2, 2]
    bilocality = InflationProblem(dag=bilocalDAG,
                                  order=blilocal_names,
                                  settings_per_party=[1, 1, 1],
                                  outcomes_per_party=[2, 2, 2],
                                  inflation_level_per_source=inflation)
    bilocalSDP           = InflationSDP(bilocality)
    bilocalSDP_commuting = InflationSDP(bilocality, commuting=True)
    test_substitutions_scenario = InflationProblem(bilocalDAG,
                                                   order=blilocal_names,
                                                   settings_per_party=[1, 2, 2],
                                                   outcomes_per_party=[3, 2, 3],
                                                   inflation_level_per_source=inflation)
    # Column structure for the NPA level 2 in a tripartite scenario
    col_structure = [[],
                     [0], [1], [2],
                     [0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [2, 2]]
    # Monomials for the NPA level 2 in the bilocality scenario
    meas = bilocalSDP.measurements
    A_1_0_0_0 = meas[0][0][0][0]
    A_2_0_0_0 = meas[0][1][0][0]
    B_1_1_0_0 = meas[1][0][0][0]
    B_1_2_0_0 = meas[1][1][0][0]
    B_2_1_0_0 = meas[1][2][0][0]
    B_2_2_0_0 = meas[1][3][0][0]
    C_0_1_0_0 = meas[2][0][0][0]
    C_0_2_0_0 = meas[2][1][0][0]
    actual_cols = [1, A_1_0_0_0, A_2_0_0_0, B_1_1_0_0, B_1_2_0_0, B_2_1_0_0,
                   B_2_2_0_0, C_0_1_0_0, C_0_2_0_0, A_1_0_0_0*A_2_0_0_0,
                   A_1_0_0_0*B_1_1_0_0, A_1_0_0_0*B_1_2_0_0,
                   A_1_0_0_0*B_2_1_0_0, A_1_0_0_0*B_2_2_0_0,
                   A_2_0_0_0*B_1_1_0_0, A_2_0_0_0*B_1_2_0_0,
                   A_2_0_0_0*B_2_1_0_0, A_2_0_0_0*B_2_2_0_0,
                   A_1_0_0_0*C_0_1_0_0, A_1_0_0_0*C_0_2_0_0,
                   A_2_0_0_0*C_0_1_0_0, A_2_0_0_0*C_0_2_0_0,
                   B_1_1_0_0*B_1_2_0_0, B_1_1_0_0*B_2_1_0_0,
                   B_1_1_0_0*B_2_2_0_0, B_1_2_0_0*B_1_1_0_0,
                   B_1_2_0_0*B_2_1_0_0, B_1_2_0_0*B_2_2_0_0,
                   B_2_1_0_0*B_1_1_0_0, B_2_1_0_0*B_2_2_0_0,
                   B_2_2_0_0*B_1_2_0_0, B_2_2_0_0*B_2_1_0_0,
                   B_1_1_0_0*C_0_1_0_0, B_1_1_0_0*C_0_2_0_0,
                   B_1_2_0_0*C_0_1_0_0, B_1_2_0_0*C_0_2_0_0,
                   B_2_1_0_0*C_0_1_0_0, B_2_1_0_0*C_0_2_0_0,
                   B_2_2_0_0*C_0_1_0_0, B_2_2_0_0*C_0_2_0_0,
                   C_0_1_0_0*C_0_2_0_0]

    def test_generating_columns_nc(self):
        truth = 41
        columns = self.bilocalSDP.build_columns(self.col_structure,
                                                return_columns_numerical=False)
        self.assertEqual(len(columns), truth,
                         "With noncommuting variables, there are  " +
                         str(len(columns)) + " columns but " + str(truth) +
                         " were expected")

    def test_generation_from_columns(self):
        columns = self.bilocalSDP.build_columns(self.actual_cols,
                                                return_columns_numerical=False)
        self.assertEqual(columns, self.actual_cols,
                         "The direct copying of columns is failing")

    def test_generation_from_lol(self):
        columns = self.bilocalSDP.build_columns(self.col_structure,
                                                return_columns_numerical=False)
        self.assertEqual(columns, self.actual_cols,
                         "Parsing a list-of-list description of columns fails")

    def test_generation_from_str(self):
        columns = self.bilocalSDP.build_columns('npa2',
                                                return_columns_numerical=False)
        self.assertEqual(columns, self.actual_cols,
                         "Parsing the string description of columns is failing")

    def test_generate_with_identities(self):
        oneParty = InflationSDP(InflationProblem(dag={"h": ["v"]},
                                                 outcomes_per_party=[2],
                                                 settings_per_party=[2],
                                                 inflation_level_per_source=[1]))
        _, columns = oneParty.build_columns([[], [0, 0]],
                                            return_columns_numerical=True)
        truth   = [[],
                   [[1, 1, 0, 0], [1, 1, 1, 0]],
                   [[1, 1, 1, 0], [1, 1, 0, 0]]]
        truth = [np.array(mon) for mon in truth]
        self.assertTrue(len(columns) == len(truth), "The number of columns is incorrect.")
        # areequal = np.all([np.array_equal(columns[i], truth[i]) for i in range(len(columns))])
        areequal = all(np.array_equiv(r[0].T, np.array(r[1]).T) for r in zip(columns, truth))
        self.assertTrue(areequal,
                         "The column generation is not capable of handling " +
                         "monomials that reduce to the identity")

    def test_generating_columns_c(self):
        truth = 37
        columns = self.bilocalSDP_commuting.build_columns(self.col_structure,
                                                 return_columns_numerical=False)
        self.assertEqual(len(columns), truth,
                         "With commuting variables, there are  " +
                         str(len(columns)) + " columns but " + str(truth) +
                         " were expected")

    # def test_nc_substitutions(self):
    #     settings = [1, 2, 2]
    #     outcomes = [3, 2, 3]
    #     scenario = InflationSDP(self.test_substitutions_scenario)
    #
    #     meas, subs, _ = scenario._generate_parties()
    #
    #     true_substitutions = {}
    #     for party in meas:
    #         # Idempotency
    #         true_substitutions = {**true_substitutions,
    #                               **{op**2: op for op in flatten(party)}}
    #         # Orthogonality
    #         for inflation in party:
    #             for measurement in inflation:
    #                 for out1 in measurement:
    #                     for out2 in measurement:
    #                         if out1 == out2:
    #                             true_substitutions[out1*out2] = out1
    #                         else:
    #                             true_substitutions[out1*out2] = 0
    #     # Commutation of different parties
    #     for A in flatten(meas[0]):
    #         for B in flatten(meas[1]):
    #             true_substitutions[B*A] = A*B
    #         for C in flatten(meas[2]):
    #             true_substitutions[C*A] = A*C
    #     for B in flatten(meas[1]):
    #         for C in flatten(meas[2]):
    #             true_substitutions[C*B] = B*C
    #     # Commutation of operators for nonoverlapping copies
    #     # Party A
    #     for copy1 in flatten(meas[0][0]):
    #         for copy2 in flatten(meas[0][1]):
    #             true_substitutions[copy2*copy1] = copy1*copy2
    #     # Party B, copies 11 and 22
    #     for copy1 in flatten(meas[1][0]):
    #         for copy2 in flatten(meas[1][3]):
    #             true_substitutions[copy2*copy1] = copy1*copy2
    #     # Party B, copies 12 and 21
    #     for copy1 in flatten(meas[1][1]):
    #         for copy2 in flatten(meas[1][2]):
    #             true_substitutions[copy2*copy1] = copy1*copy2
    #     # Party C
    #     for copy1 in flatten(meas[2][0]):
    #         for copy2 in flatten(meas[2][1]):
    #             true_substitutions[copy2*copy1] = copy1*copy2
    #
    #     self.assertDictEqual(subs, true_substitutions)


    # def test_c_substitutions(self):
    #     scenario = InflationSDP(self.test_substitutions_scenario,
    #                             commuting=True)
    #     meas, subs, _ = scenario._generate_parties()
    #
    #     true_substitutions = {}
    #
    #     flatmeas = flatten(meas)
    #     #for m1, m2 in itertools.product(flatmeas, flatmeas):
    #     for i in range(len(flatmeas)):
    #         for j in range(i, len(flatmeas)):
    #             m1 = flatmeas[i]
    #             m2 = flatmeas[j]
    #             if str(m1) > str(m2):
    #                 true_substitutions[m1*m2] = m2*m1
    #             elif str(m1) < str(m2):
    #                 true_substitutions[m2*m1] = m1*m2
    #             else:
    #                 pass
    #     for party in meas:
    #         # Idempotency
    #         true_substitutions = {**true_substitutions,
    #                               **{op**2: op for op in flatten(party)}}
    #         # Orthogonality
    #         for inflation in party:
    #             for measurement in inflation:
    #                 for out1 in measurement:
    #                     for out2 in measurement:
    #                         if out1 == out2:
    #                             true_substitutions[out1*out2] = out1
    #                         else:
    #                             true_substitutions[out1*out2] = 0
    #
    #     self.assertEqual(len(subs), len(true_substitutions), "The number of substitutions is incorrect")
    #
    #     for k1, v1 in true_substitutions.items():
    #         self.assertEqual(subs[k1], v1, "Substitution " + str(k1) + " is incorrect")
    #
    #
    #     self.assertDictEqual(subs, true_substitutions)

# class TestInflation(unittest.TestCase):
    # def test_commutations_after_symmetrization(self):
    #     from causalinflation.quantum.fast_npa import nb_commuting
    #
    #     scenario = InflationSDP(InflationProblem(dag={"h": ["v"]},
    #                                              outcomes_per_party=[2],
    #                                              settings_per_party=[2],
    #                                              inflation_level_per_source=[2]
    #                                              ),
    #                             commuting=True)
    #     meas, subs, names = scenario._generate_parties()
    #     col_structure = [[], [0, 0]]
    #     flatmeas = np.array(flatten(meas))
    #     measnames = np.array([str(meas) for meas in flatmeas])
    #
    #     lexorder = np.array([[1, 1, 0, 0],
    #                          [1, 1, 1, 0],
    #                          [1, 2, 0, 0],
    #                          [1, 2, 1, 0]])
    #     notcomm = np.zeros((lexorder.shape[0], lexorder.shape[0]), dtype=int)
    #     for i in range(lexorder.shape[0]):
    #         for j in range(i+1, lexorder.shape[0]):
    #             notcomm[i, j] = int(not nb_commuting(lexorder[i],
    #                                                                lexorder[j]))
    #
    #     # notcomm = np.zeros((lexorder.shape[0], lexorder.shape[0]), dtype=int)
    #     # notcomm[0, 1] = 1
    #     # notcomm[2, 3] = 1
    #     # notcomm = notcomm + notcomm.T
    #
    #     # Define moment matrix columns
    #     _, ordered_cols_num = scenario.build_columns(col_structure,
    #                                               return_columns_numerical=True)
    #
    #     expected = [[[0]],
    #                 [[1, 2, 0, 0], [1, 2, 1, 0]],
    #                 [[1, 1, 0, 0], [1, 2, 0, 0]],
    #                 [[1, 1, 1, 0], [1, 2, 0, 0]],
    #                 [[1, 1, 0, 0], [1, 2, 1, 0]],
    #                 [[1, 1, 1, 0], [1, 2, 1, 0]],
    #                 [[1, 1, 0, 0], [1, 1, 1, 0]]]
    #
    #     permuted_cols = apply_source_permutation_coord_input(ordered_cols_num,
    #                                                          0,
    #                                                          [1, 0],
    #                                                          False,
    #                                                          notcomm,
    #                                                          lexorder)
    #     self.assertTrue(np.array_equal(np.array(expected[5]), permuted_cols[5]),
    #                      "The commuting relations of different copies are not "
    #                      + "being applied properly after inflation symmetries")

class TestSDPOutput(unittest.TestCase):
    def GHZ(self, v):
        dist = np.zeros((2,2,2,1,1,1))
        for a in [0, 1]:
            for b in [0, 1]:
                for c in [0, 1]:
                    if (a == b) and (b == c):
                        dist[a,b,c,0,0,0] = v/2 + (1-v)/8
                    else:
                        dist[a,b,c,0,0,0] = (1-v)/8
        return dist

    cutInflation = InflationProblem({"lambda": ["A", "B"],
                                     "mu": ["B", "C"],
                                     "sigma": ["A", "C"]},
                                     order=['A', 'B', 'C'],
                                     outcomes_per_party=[2, 2, 2],
                                     settings_per_party=[1, 1, 1],
                                     inflation_level_per_source=[2, 1, 1])

    def test_CHSH(self):
        bellScenario = InflationProblem({"lambda": ["A", "B"]},
                                         order=("A", "B"),
                                         outcomes_per_party=[2, 2],
                                         settings_per_party=[2, 2],
                                         inflation_level_per_source=[1])
        sdp = InflationSDP(bellScenario)
        sdp.generate_relaxation('npa1')
        self.assertEqual(len(sdp.generating_monomials), 5,
                         "The number of generating columns is not correct")
        self.assertEqual(sdp.n_knowable, 8 + 1,  # only '1' is included here. No orthogonal moments in CG notation with one outcome.
                         "The count of knowable moments is wrong")
        self.assertEqual(sdp.n_unknowable, 2,
                         "The count of unknowable moments is wrong")
        meas = sdp.measurements
        A0 = 2*meas[0][0][0][0] - 1
        A1 = 2*meas[0][0][1][0] - 1
        B0 = 2*meas[1][0][0][0] - 1
        B1 = 2*meas[1][0][1][0] - 1

        sdp.set_objective(A0*(B0+B1)+A1*(B0-B1), 'max')
        self.assertEqual(len(sdp._objective_as_name_dict), 7,
                         "The parsing of the objective function is failing")
        sdp.solve()
        self.assertTrue(np.isclose(sdp.objective_value, 2*np.sqrt(2)),
                        "The SDP is not recovering max(CHSH) = 2*sqrt(2)")
        # bias = 3/4
        # biased_chsh = 2.62132    # Value obtained by other means (ncpol2sdpa)
        # sdp.set_values({meas[0][0][0][0]: bias,    # Variable for p(a=0|x=0)
        #                 'A_1_1_0': bias,           # Variable for p(a=0|x=1)
        #                 meas[1][0][0][0]: bias,    # Variable for p(b=0|y=0)
        #                 'B_1_1_0': bias            # Variable for p(b=0|y=1)
        #                 })
        # sdp.solve()
        # self.assertTrue(np.isclose(sdp.objective_value, biased_chsh),
        #                 f"The SDP is not recovering max(CHSH) = {biased_chsh} "
        #                 + "when the single-party marginals are biased towards "
        #                 + str(bias))

    def test_GHZ_NC(self):
        sdp = InflationSDP(self.cutInflation)
        sdp.generate_relaxation('local1')
        self.assertEqual(sdp.One.name, '1', "The unit monomial is not being named correctly.")
        self.assertEqual(len(sdp.generating_monomials), 18,
                         "The number of generating columns is not correct")
        self.assertEqual(sdp.n_knowable, 8 + 1,  # only '1' is included here. No orthogonal moments in CG notation with one outcome.
                         "The count of knowable moments is wrong")
        self.assertEqual(sdp.n_unknowable, 13,
                         "The count of unknowable moments is wrong")

        sdp.set_distribution(self.GHZ(0.5 + 1e-2))
        # print(sdp.known_moments)
        # for mon in sdp.list_of_monomials:
        #     print(f"{mon.idx}: = {mon.name} (aka:) {mon.factors}")
        # get_mon_9 = [mon.name for mon in sdp.list_of_monomials if mon.idx == 9]
        # print(get_mon_9[0])
        # self.assertEqual(sdp.known_moments_idx_dict[9],
        #                  (0.5+1e-2) / 2 + (0.5-1e-2) / 8,
        #                  "Setting the distribution is failing")
        known_value = (0.5+1e-2) / 2 + (0.5-1e-2) / 8
        # print("Known value: ", known_value)
        # print(sdp.known_moments_name_dict)
        self.assertIn(known_value,
                        sdp.known_moments_name_dict.values(),
                         "Setting the distribution is failing")
        # print(sdp.known_moments_name_dict)
        sdp.solve()
        self.assertEqual(sdp.status, 'infeasible',
                     "The NC SDP is not identifying incompatible distributions")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective <= 0,
                        "The NC SDP with feasibility as optimization is not " +
                        "identifying incompatible distributions")
        sdp.set_distribution(self.GHZ(0.5 - 1e-4))
        # self.assertEqual(sdp.known_moments_idx_dict[9],
        #                  (0.5-1e-4) / 2 + (0.5+1e-4) / 8,
        #                  "Re-setting the distribution is failing")
        known_value = (0.5 - 1e-4) / 2 + (0.5 + 1e-4) / 8
        # print("Known value: ", known_value)
        # print(sdp.known_moments_name_dict)
        self.assertIn(known_value,
                        sdp.known_moments_name_dict.values(),
                         "Setting the distribution is failing")
        sdp.solve()
        self.assertEqual(sdp.status, 'feasible',
                       "The NC SDP is not recognizing compatible distributions")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective >= 0,
                        "The NC SDP with feasibility as optimization is not " +
                        "recognizing compatible distributions")

    def test_GHZ_commuting(self):
        sdp = InflationSDP(self.cutInflation, commuting=True)
        sdp.generate_relaxation('local1')
        self.assertEqual(len(sdp.generating_monomials), 18,
                         "The number of generating columns is not correct")
        self.assertEqual(sdp.n_knowable, 8 + 1,  # only '1' is included here. No orthogonal moments in CG notation with one outcome.
                         "The count of knowable moments is wrong")
        self.assertEqual(sdp.n_unknowable, 11,
                         "The count of unknowable moments is wrong")

        sdp.set_distribution(self.GHZ(0.5 + 1e-2))
        sdp.solve()
        self.assertEqual(sdp.status, 'infeasible',
              "The commuting SDP is not identifying incompatible distributions")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective <= 0,
                        "The commuting SDP with feasibility as optimization " +
                        "is not identifying incompatible distributions")
        sdp.set_distribution(self.GHZ(0.5 - 1e-2))
        sdp.solve()
        self.assertEqual(sdp.status, 'feasible',
                "The commuting SDP is not recognizing compatible distributions")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective >= 0,
                        "The commuting SDP with feasibility as optimization " +
                        "is not recognizing compatible distributions")

    def test_lpi_bounds(self):
        sdp = InflationSDP(
                  InflationProblem({"h1": ["A", "B"],
                                    "h2": ["B", "C"],
                                    "h3": ["A", "C"]},
                                    outcomes_per_party=[2, 2, 2],
                                    settings_per_party=[1, 1, 1],
                                    inflation_level_per_source=[3, 3, 3],
                                    order=('A', 'B', 'C')),
                            commuting=False)
        cols = [np.array([]),
                np.array([[1, 1, 0, 1, 0, 0]]),
                np.array([[2, 2, 1, 0, 0, 0],
                          [2, 3, 1, 0, 0, 0]]),
                np.array([[3, 0, 2, 2, 0, 0],
                          [3, 0, 3, 2, 0, 0]]),
                np.array([[1, 1, 0, 1, 0, 0],
                          [2, 2, 1, 0, 0, 0],
                          [2, 3, 1, 0, 0, 0],
                          [3, 0, 2, 2, 0, 0],
                          [3, 0, 3, 2, 0, 0]]),
        ]
        sdp.generate_relaxation(cols) 
        sdp.set_distribution(self.GHZ(0.5), use_lpi_constraints=True)
        semiknown_coeffs = np.array([v[0] for k, v in sdp.semiknown_moments.items()])
        self.assertTrue(len(sdp.semiknown_moments) > 1,
                        ("This example is explicitly chosen to check semiknowns."))
        self.assertTrue(np.all(semiknown_coeffs <= 1),
                    ("All known coefficients should be between zero and one."))
        # print(list(sdp.semiknown_moments.items()))