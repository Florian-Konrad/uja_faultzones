[Mesh]
  type = FileMesh
  boundary_id = '1 2 4 3 5 6'
  boundary_name = 'bottom top north east south west'
  file = 35m_scaled.e
[]

[GlobalParams]
  variable = pore_pressure
  matrix_seperation_according_to_subdomains = false
  initial_rb_userobject = initializeRBSystem
  simulation_type = transient
[]

[Variables]
  [./pore_pressure]
  [../]
[]

[MeshModifiers]
  [./corner_node]
    type = AddExtraNodeset
    new_boundary = 'pinned_node'
    coord = '0.0 0.0 0.0'
  [../]
[]

# For stabilization of the system, does not effect the results
[BCs]
  [./stabilize]
    type = DwarfElephantRBDirichletBC
    value = 0.0
    boundary = 'pinned_node' # south east west'
  [../]
[]

[Kernels]
  [./DarcyMatrix]
    type = DwarfElephantRBDiffusion
    block = 0
    ID_Aq = 0
  [../]
  [./DarcyFault]
    type = DwarfElephantRBDiffusion
    ID_Aq = 1
    block = 1
  [../]
  [./DarcyWell]
    type = DwarfElephantRBDarcy
    ID_Aq = 2
    # k_well*pi*r_well*r_well*char_stress
    # k_well = permeability of the well (1e-7 m^2)
    # r_well = radius of the well (0.2 m)
    # char_stress = refernence pressure (1e6 Pa)
    permeability = 1.39626340e-11
    block = 2
  [../]
  ## Lifting function is used for the initial conditions
  #[./LiftingICMatrix]
  #  type = DwarfElephantRBLiftingFunctionKernel
  #  lifting_function = p_ini_func
  #  ID_Fq = 0
  #  block = 0
  #[../]
  #[./LiftingICFault]
  #  type = DwarfElephantRBLiftingFunctionKernel
  #  lifting_function = p_ini_func
  #  ID_Fq = 1
  #  block = 1
  #[../]
  #[./LiftingICWell]
  #  type = DwarfElephantRBLiftingFunctionKernelWithParameterIndependentScale
  #  lifting_function = p_ini_func
  #  # k_well*pi*r_well*r_well*char_stress
  #  # k_well = permeability of the well (1e-7 m^2)
  #  # r_well = radius of the well (0.2 m)
  #  # char_stress = refernence pressure (1e6 Pa)
  #  scale = 1.2566370614359173e-02
  #  ID_Fq = 2
  #  block = 2
  #[../]
  [./StorageTermMatrix]
    type = DwarfElephantRBTimeDerivative
    block = 0
    ID_Mq = 0
  [../]
  [./StorageTermFault]
    type = DwarfElephantRBTimeDerivative
    ID_Mq = 1
    block = 1
  [../]
  [./StorageTermWell]
    type = DwarfElephantRBConstantSpecificStorage
    ID_Mq = 2
    # S_s,well*char_stress*char_length*char_length
    # char_length = reference length (30000 m)
    specific_storage = 2.51327412e-10
    block = 2
  [../]
[]


[DiracKernels]
  [./Produktion]
    type = DwarfElephantRBPointSource
    point = '0.5 0.5 -0.01666666'
    ID_Fq = 1#3
    sink = true
  [../]
[]

[Problem]
  type = DwarfElephantRBProblem
[]

[Functions]
  [./p_ini_func]
    vals = '1e+5 971.82 9.81 3000 1.0e+06 30000'
    type = ParsedFunction
    vars = 'p0 rho_f g GW char_stress char_length'
    # value = '(p0-rho_f*g*(z*char_length-GW))/char_stress'
    value = 'rho_f*g*GW/char_stress'
  [../]
[]

[RBTimeStepper]
  [./GrowthRate]
    growth_rate = 1.1
  [../]
[]

[RBTimeDependentMu]
  [./RBStartEndTimeMu]
    start_time = 1
    end_time = 1.8e6
    ID_time_dependent_param = 5
  [../]
[]

[UserObjects]
  [./initializeRBSystem]
    type = DwarfElephantInitializeRBSystemTransient
    execute_on = 'initial'
    N_max = 200   # maximum number of basis functions
    n_training_samples = 1000   # number of training samples
    rel_training_tolerance = 1.e-3  # approximation accuracy
    n_time_steps = 127
    delta_t = 1
    euler_theta = 1       # 1 = backward euler
    # parameters: mu_0 = k_matrix, mu_1 = k_faultzone, mu_2 = visocisty,
    #             mu_3 = S_s,matrix, mu_4 = S_s,faultzone, mu_5 = production rate
    # reference parameters for permeability and specific storage see Kernel block
    # production rate: in_out_rate/(rho_f*char_length)
    parameter_names = 'mu_0 mu_1 mu_2 mu_3 mu_4 mu_5'    #Please name them mu_0 , mu_1 , ..., mu_n for the reusability
    parameter_min_values = '1.0e-11 1.0e-08 1.0e-4 1.80e+03 1.80e+03 3.4299904646265100e-07'
    parameter_max_values = '2.0e-05 1.0e-03 3.0e-4 1.44e+05 1.44e+05 6.859980929253016e-07'
    normalize_rb_bound_in_greedy = true
    training_parameters_random_seed = 200   # for reproducibility
    time_dependent_parameter = true
    # start_time = 1      # start time of the production
    # end_time = 1.8e6    # end time of the production
    # ID_time_dependent_param = 5 # ID of the time depedent parameter
    varying_timesteps = true    # for allowing a growing dt
    # growth_rate = 1.1
    nonzero_initialization = false  # we start with zero as an intial condition because of the lifting function
  [../]
  [./FoerderDruck]
    type = DwarfElephantRBPointValue
    point = '0.5 0.5 -0.01666666'
    outputid = 0
  [../]
  [./performRBSystem]
    type = DwarfElephantOfflineOnlineStageTransient
    online_mu = '1.0e-5 1.0e-04 0.00028974 1.8e3 1.8e3 6.859980929253016e-07'
    execute_on = 'timestep_end'
    online_stage = true
    output_file = true
    output_console = true
  [../]
[]

[Preconditioning]
    [./hypre]
      petsc_options_iname = '-ksp_type -ksp_rtol -ksp_max_it -pc_type -pc_hypre_type
                             -snes_type -snes_linesearch_type -snes_atol -snes_rtol
                             -snes_max_it -ksp_gmres_restart'
      full = true
      type = SMP
      petsc_options_value = 'fgmres 1e-13 100 hypre boomeramg
                             newtonls basic 1e-12 1e-4
                             25 30'
      petsc_options = '-snes_ksp_ew -snes_monitor -snes_linesearch_monitor -snes_converged_reason'
    [../]
[]


[Executioner]
  type = DwarfElephantRBExecutioner
  solve_type = Newton
  l_tol = 1e-08
  nl_rel_tol = 1e-08
[]

[Outputs]
  execute_on = 'timestep_end'
  csv = true
  perf_graph = false
  [./Exodus]
    type = Exodus
  [../]
  [./console]
    type = Console
    outlier_variable_norms = false
  [../]
[]
