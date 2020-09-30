

import numpy as np
import scipy.linalg as la
import xdrlib


    

class OnlineStage():
    
    
    def read_offline_data(self):
        """This method is responsible for reading all offline data that are
            necessary for calculating the output of interest without the output
            error bounds.

           Args:
                path_offline_data = path to the offline data folder
                q_a = number of stiffness matrices (A)
                q_f = number of load vectors (f)
                q_l = number of attached theta objects to each output vector
                n_outputs = number of output vectors (l)

            Returns:
                n_bfs = number of basis functions
                RB_Aq = reduced stiffness matrices
                RB_Fq = reduced load vectors
                RB_Oq = reduced load vectors

        """
        # number of basis functions
        with open(self.path_offline_data + '/n_bfs.xdr', 'rb') as f_reader: 
            f = f_reader.read()
            n_bfs = xdrlib.Unpacker(f).unpack_int()

        # RB_Aq
        RB_Aq = np.empty([n_bfs, n_bfs, self.q_a])
        for i in range(self.q_a):
            f = open('{}/RB_A_{}.xdr'.format(self.path_offline_data, str(i).zfill(3)), 'rb').read()
            u = xdrlib.Unpacker(f)
            orig_array = u.unpack_farray(n_bfs*n_bfs,u.unpack_double) 
            temp = np.reshape(orig_array,[n_bfs,n_bfs])
            RB_Aq[:,:,i] = temp

        # RB_Fq
        RB_Fq = np.empty([n_bfs, self.q_f])
        for i in range(self.q_f):
            f = open('{}/RB_F_{}.xdr'.format(self.path_offline_data, str(i).zfill(3)), 'rb').read()
            u = xdrlib.Unpacker(f)
            RB_Fq[:,i] = u.unpack_farray(n_bfs,u.unpack_double)

        # RB_Oq
        RB_Oq = np.empty([n_bfs, self.n_outputs, self.q_l]) 
        for i in range(self.n_outputs):
            for j in range(self.q_l):
                f = open("{}/output_{}_{}.xdr".format(self.path_offline_data, 
                        str(i).zfill(3), str(j).zfill(3)), 'rb').read() 
                u = xdrlib.Unpacker(f)
                RB_Oq[:,i,j] = u.unpack_farray(n_bfs,u.unpack_double)

        return (n_bfs, RB_Aq, RB_Fq, RB_Oq)
    
    def read_transient_offline_data(self,parameter_dependent_IC = False, q_ic = 0):
        """This method is responsible for reading all offline data that are
           additionally necessary for the transient output of interest without the
           output error bounds.

           Args:
                self.path_offline_data = path to the transient offline data folder
                q_m = number of mass matrices (M)
                n_bfs = number of basis functions
                parameter_dependent_IC = determines whether the initial conditions
                                     are parameter dependent or note
                q_ic = number of intial conditions (IC)

            Returns:
                RB_Mq = reduced mass matrices
                initial_conditions = initial conditions
                RB_L2_matrix = reduced L2 matrix (only returned if
                           parameter_dependent_IC = True)

        """
        # RB_Mq
        RB_Mq = np.ndarray([self.n_bfs, self.n_bfs, self.q_m])
        if(parameter_dependent_IC==True):
            initial_conditions = np.ndarray([self.n_bfs, q_ic])
            RB_L2_matrix = np.ndarray([self.n_bfs, self.n_bfs])

        for i in range(self.q_m):
            #f = open('{}/RB_M_{}.xdr'.format(self.path_offline_data, str(i).zfill(3)), 'rb').read()
            f = open(self.path_transient_offline_data + '/RB_M_00' + str(i) + '.xdr', 'rb').read()
            u = xdrlib.Unpacker(f)
            RB_Mq[:,:,i] = np.reshape(u.unpack_farray(self.n_bfs*self.n_bfs,u.unpack_double),
                                  [self.n_bfs,self.n_bfs])

        # intial conditions
        # currently it is only supported if online_N = n_bfs
        if(parameter_dependent_IC == False):
            # initial_conditions = np.ndarray([40,1])
            f = open(self.path_transient_offline_data + '/initial_conditions.xdr', 'rb').read()
            u = xdrlib.Unpacker(f)
            position = np.sum(np.arange(1,self.n_bfs,1))

            initial_conditions = u.unpack_farray(position+self.n_bfs,u.unpack_double)
            initial_conditions = initial_conditions[position:]

            return (RB_Mq, initial_conditions)

        else:
            for i in range(q_ic):
                f = open('{}/RB_IC_{}.xdr'.format(self.path_offline_data, str(i).zfill(3)), 'rb').read()
                u = xdrlib.Unpacker(f)
                initial_conditions[:,i] = u.unpack_farray(self.n_bfs,u.unpack_double)

            f = open(self.path_transient_offline_data + '/RB_L2_matrix.xdr').read()
            u = xdrlib.Unpacker(f)
            RB_L2_matrix = np.reshape(u.unpack_farray(self.n_bfs*self.n_bfs, u.unpack_double),
                                       [self.n_bfs,self.n_bfs])

            return (RB_Mq, initial_conditions, RB_L2_matrix)
        
    def transient_rb_solve_without_error_bound(self, online_mu_parameters):

        """This method is responsible performing the transient rb solve without the
           output error bounds.

           Args:
               online_mu_parameters = online parameters
               q_a = number of stiffness matrices (A)
               q_m = number of mass matrices (M)
               q_f = number of load vectors (f)
               q_l = number of attached theta objects to each output vector
               n_outputs = number of output vectors (l)
               online_N = the number of basis functions that should be considered
               n_timesteps = number of time steps
               dt = time step size
               euler_theta = Time stepping scheme
               RB_Aq = reduced stiffness matrices
               RB_Mq = reduced mass matrices
               RB_Fq = reduced load vectors
               RB_Oq = reduced load vectors
               initial_conditions = initial conditions
               parameter_dependent_IC = determines whether the initial conditions
                                    are parameter dependent or note
               q_ic = number of intial conditions (IC)
               RB_L2_matrix = reduced L2 matrix

            Returns:
                RB_outputs_all_k = the output of interest for all timesteps

        """
        # assemble the mass matrix
        # RB_mass_matrix_N = np.zeros([online_N, online_N])
        if(self.time_dependent_parameters == True):
            time = 0;
            online_mu_parameters_initial = np.zeros([len(online_mu_parameters)])
            for i in range (len(online_mu_parameters)):
                online_mu_parameters_initial[i] = online_mu_parameters[i]
            online_mu_parameters = self.calculate_time_dependent_mu(online_mu_parameters, online_mu_parameters_initial,
                                                           time, self.ID_param, self.dt,
                                                           self.start_time,self.end_time)

        RB_mass_matrix_N = np.sum(self.RB_Mq*self.theta_M(online_mu_parameters), axis = 2)

        # assemble LHS matrix
        # RB_LHS_matrix = np.zeros([online_N, online_N])
        RB_LHS_matrix = RB_mass_matrix_N * (1./self.dt)
        RB_LHS_matrix += np.sum(self.RB_Aq*self.theta_A(online_mu_parameters), axis = 2)

        # assemble RHS matrix
        # RB_RHS_matrix = np.zeros([online_N, online_N])
        RB_RHS_matrix = RB_mass_matrix_N * (1./self.dt)
        RB_RHS_matrix += np.sum(-(1.-self.euler_theta)*self.RB_Aq*self.theta_A(online_mu_parameters), axis = 2)

        # add forcing terms
        RB_RHS_save = np.zeros([self.online_N])
        RB_RHS_save += np.sum(self.RB_Fq*self.theta_F(online_mu_parameters), axis = 1)

        # add the intial conditions to the solution vector
        RB_solution = np.zeros([self.online_N, 1])

        if(self.parameter_dependent_IC==False):
            RB_solution = self.initial_conditions
        #else:
            # RB_rhs_N= np.zeros([online_N,1]);
            #RB_rhs_N += self.initial_conditions*self.theta_IC(online_mu_parameters)
            #RB_solution = la.lu_solve(la.lu_factor(self.RB_L2_matrix), RB_rhs_N)
            #RB_solution = RB_solution[:,0]

        old_RB_solution = np.zeros([self.online_N, 1])

        # initialize the RB rhs
        # RB_rhs = np.zeros([online_N,1])

        # initialize the vectors storing the solution data
        RB_temporal_solution_data = np.zeros([self.n_timesteps+1,self.online_N])

        # load the initial data
        RB_temporal_solution_data[0] = RB_solution

        # set outputs at initial time
        RB_outputs_all_k = np.zeros([self.n_outputs, self.n_timesteps+1])

        RB_outputs_all_k[:,0] = np.sum(np.reshape(RB_solution, [self.online_N, 1])*
                                       (self.RB_Oq[:,:,0]*self.theta_O(online_mu_parameters)), axis=0)
        
        initial_dt = self.dt
        
        for i in range(1,self.n_timesteps+1):
            if(self.varying_timesteps==True and self.time_dependent_parameters == False):
                # assemble LHS matrix
                # RB_LHS_matrix = np.zeros([online_N, online_N])
                RB_LHS_matrix = RB_mass_matrix_N * (1./self.dt)
                RB_LHS_matrix += np.sum(self.RB_Aq*self.theta_A(online_mu_parameters), axis = 2)

                # assemble RHS matrix
                # RB_RHS_matrix = np.zeros([online_N, online_N])
                RB_RHS_matrix = RB_mass_matrix_N * (1./self.dt)
                RB_RHS_matrix += np.sum(-(1.-self.euler_theta)*self.RB_Aq*self.theta_A(online_mu_parameters), axis = 2)
            elif((self.varying_timesteps==False and self.time_dependent_parameters == True) or (self.varying_timesteps==True and self.time_dependent_parameters==True)):
                time +=self.dt
                online_mu_parameters = self.calculate_time_dependent_mu(online_mu_parameters, online_mu_parameters_initial,
                                                               time, self.ID_param, self.dt,
                                                               self.start_time,self.end_time)
                RB_mass_matrix_N = np.sum(self.RB_Mq*self.theta_M(online_mu_parameters), axis = 2)

                # assemble LHS matrix
                # RB_LHS_matrix = np.zeros([online_N, online_N])
                RB_LHS_matrix = RB_mass_matrix_N * (1./self.dt)
                RB_LHS_matrix += np.sum(self.RB_Aq*self.theta_A(online_mu_parameters), axis = 2)

                # assemble RHS matrix
                # RB_RHS_matrix = np.zeros([online_N, online_N])
                RB_RHS_matrix = RB_mass_matrix_N * (1./self.dt)
                RB_RHS_matrix += np.sum(-(1.-self.euler_theta)*self.RB_Aq*self.theta_A(online_mu_parameters), axis = 2)

                # add forcing terms
                RB_RHS_save = np.zeros([self.online_N])
                RB_RHS_save += np.sum(self.RB_Fq*self.theta_F(online_mu_parameters), axis = 1)

            old_RB_solution = RB_solution

            RB_rhs = np.dot(RB_RHS_matrix, old_RB_solution)

            # add forcing term
            RB_rhs += self.get_control(i)*RB_RHS_save

            RB_solution = la.lu_solve(la.lu_factor(RB_LHS_matrix), RB_rhs)

            # Save RB_solution for current time level
            RB_temporal_solution_data[i] = RB_solution;

            RB_outputs_all_k[:,i] = np.sum(np.reshape(RB_solution, [self.online_N, 1])*
                                       (self.RB_Oq[:,:,0]*self.theta_O(online_mu_parameters)), axis=0)

            if(self.dt < self.threshold):
                self.dt*=self.growth_rate
            
            if(self.time_dependent_parameters == True):
                for i in range (len(online_mu_parameters)):
                    online_mu_parameters[i] = online_mu_parameters_initial[i]
        
        #resetting dt to intial otherwise it gets bigger every time the rb_model_object is called for a transient solve:
        self.dt = initial_dt
        
        return (RB_outputs_all_k)
    
    def calculate_time_dependent_mu(self,online_mu_parameters, online_mu_parameters_initial, time, ID_param, dt,
                                start_time, end_time):

        pre_factor = 1.0
        if (time < start_time or time - dt >= end_time):
            pre_factor = 0.0
        elif (time - dt < start_time):
            if (time <= end_time):
                pre_factor *= (time - start_time) / dt
            else:
                pre_factor *= (end_time - start_time) / dt
        elif (time > end_time):
            pre_factor *= (end_time - (time - dt)) / dt

        for i in range(len(ID_param)):
            online_mu_parameters[ID_param[i]] = pre_factor * online_mu_parameters_initial[ID_param[i]]

        return online_mu_parameters
    
    
    
    
    
class model_from_offline_data(OnlineStage):
    
    def __init__(self,
                 path_offline_data,
                 q_a,q_f,q_l,q_m,
                 n_outputs,
                 n_timesteps,
                 dt,
                 euler_theta,
                 varying_timesteps = False,
                 growth_rate = 1.0,
                 time_dependent_parameters = False,
                 ID_param = [0],
                 start_time = 0.0,
                 end_time = 0.0,
                 parameter_dependent_IC = False,
                 q_ic = 0,
                 RB_L2_matrix = 0,
                 threshold = 1.0e30):
        self.path_offline_data=path_offline_data
        self.path_transient_offline_data=path_offline_data
        self.q_a=q_a
        self.q_f=q_f
        self.q_l=q_l
        self.q_m=q_m
        self.n_outputs=n_outputs
        [self.online_N, self.RB_Aq, self.RB_Fq, self.RB_Oq] = self.read_offline_data()
        self.n_bfs=self.online_N
        [self.RB_Mq, self.initial_conditions] = self.read_transient_offline_data()
        self.n_timesteps=n_timesteps
        self.dt=dt
        self.euler_theta=euler_theta
        self.varying_timesteps = varying_timesteps
        self.growth_rate = growth_rate
        self.time_dependent_parameters = time_dependent_parameters
        self.ID_param = ID_param
        self.start_time = start_time
        self.end_time = end_time
        self.parameter_dependent_IC = parameter_dependent_IC
        self.q_ic = q_ic
        self.RB_L2_matrix = RB_L2_matrix
        self.threshold = threshold

                                              
        
    
#['k_matrix','k_fault','visocisty','S_matrix','S_fault','rate']
#['k_matrix','visocisty','S_matrix','rate']
    def theta_A (self,online_mu_parameters):
        if len(online_mu_parameters) == 6:
            return [online_mu_parameters[0]/online_mu_parameters[2], online_mu_parameters[1]/online_mu_parameters[2],
                    1.0/online_mu_parameters[2]]
        elif len(online_mu_parameters) == 4:
            return [online_mu_parameters[0]/online_mu_parameters[1],
                    1.0/online_mu_parameters[1]]  
        else:
            print('length of online_mu_parameters not 4 and not 6')
    
    def theta_F (self, online_mu_parameters):
        if len(online_mu_parameters) == 6:
            return [1.0, online_mu_parameters[5]]
        elif len(online_mu_parameters) == 4:
            return [1.0, online_mu_parameters[3]]
        else:
            print('length of online_mu_parameters not 4 and not 6')
            
    def theta_M(self, online_mu_parameters):
        if len(online_mu_parameters) == 6:
            return [online_mu_parameters[3], online_mu_parameters[4], 1.0]
        elif len(online_mu_parameters) == 4:
            return [online_mu_parameters[2], 1.0]
        else:
            print('length of online_mu_parameters not 4 and not 6')
    
    def theta_O (self, online_mu_parameters):
        return [1.0]
    
    def get_control(self,time_level):
        return 1.0
    
    def stability_lower_bound(self,online_mu_parameters):
        return np.min(self.theta_A(online_mu_parameters))
    
    