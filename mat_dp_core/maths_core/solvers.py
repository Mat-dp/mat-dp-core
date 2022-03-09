from functools import reduce
from typing import List, Optional, Tuple, Union

import numpy as np
from numpy import ndarray

from .constraints import EqConstraint, LeConstraint
from .processes import Process, Processes, ProcessExpr
from .resources import Resources
from .solve import solve


def construct_resource_matrix(
    process_produces: ndarray, run_vector: ndarray
) -> ndarray:
    """
    process_produces - A (resource, process) array describing the resources consumed
    and produced by each process
    run_vector - A (process) vector displaying the runs of each process

    returns the resource_matrix (resource, process), the resource produced or consumed by each process
    """
    return (
        np.full(
            process_produces.shape,
            run_vector,
        )
        * process_produces
    )


def construct_flow_matrix(resource_matrix: ndarray) -> ndarray:
    """
    resource_matrix - A (resource, process) array describing the resource
    produced or consumed by each process

    returns the flow_matrix (resource, process1, process2), the flow in a particular resource
    from process1 to process2
    """
    total_res_produced_vector = np.sum(
        resource_matrix, where=resource_matrix > 0, axis=1
    )
    produced = np.where(resource_matrix > 0, resource_matrix, 0)
    consumed = np.where(resource_matrix < 0, resource_matrix, 0)
    reciprocal_total_res = np.reciprocal(
        total_res_produced_vector,
        where=total_res_produced_vector != 0,
        dtype=float,
    )
    unreflected_flow_matrix = np.einsum(
        "i, ij, ik -> ijk", reciprocal_total_res, consumed, produced
    )
    return np.subtract(
        unreflected_flow_matrix,
        np.transpose(unreflected_flow_matrix, axes=(0, 2, 1)),
    )


def construct_cumulative_resource_matrix(
    resources: Resources,
    processes: Processes,
    run_vector: ndarray,
    allow_inconsistent_order_of_mag: bool,
) -> ndarray:
    """
    resources - The resources object
    processes - The processes object
    run_vector - the vector of processes describing the solution from __init__
    allow_inconsistent_order_of_mag - boolean that allows the solver to ignore inconsistent orders
    of magnitude

    returns a cumulative_resource_matrix (resource, process) describing the total resource used
    by each process
    """

    def make_eq_constraints(
        production_matrix: ndarray,
        processes: Processes,
        run_vector: ndarray,
    ) -> List[EqConstraint]:
        def make_eq_constraint(
            process1: Process, process2: Process, p2_over_p1: float
        ) -> EqConstraint:
            """
            Given two processes and the ratio between them make an eq_constraint.
            """
            return EqConstraint(
                f"{process1.name}_{process2.name}_1:{p2_over_p1}ratio",
                process1 - p2_over_p1 * process2,
                0,
            )

        def identify_process_index_pairs(
            production_matrix,
        ) -> List[Tuple[int, int]]:
            """
            Identify pairs of process indices that both produce the same resource
            """
            final_pairs = []
            for resource in production_matrix:
                non_zero_elems = np.nonzero(resource)[0]
                if len(non_zero_elems) > 1:
                    pairs = [
                        (non_zero_elems[0], i) for i in non_zero_elems[1:]
                    ]
                    final_pairs += pairs
            return final_pairs

        process_pairs = identify_process_index_pairs(production_matrix)

        eq_constraints = []
        for process1_index, process2_index in process_pairs:
            process1 = processes[int(process1_index)]
            process2 = processes[int(process2_index)]
            process1_runs = run_vector[process1_index]
            process2_runs = run_vector[process2_index]
            p2_over_p1 = process2_runs / process1_runs
            eq_constraints.append(
                make_eq_constraint(process1, process2, p2_over_p1)
            )
        return eq_constraints

    objective: ProcessExpr = reduce(
        lambda x, y: x + y,
        [process * 1 for process in processes],
    )
    production_matrix = np.where(
        processes.process_produces > 0,
        processes.process_produces,
        0,
    )
    eq_cons = make_eq_constraints(production_matrix, processes, run_vector)
    process_process_matrix = np.array(
        [
            solve(
                resources,
                processes,
                use_process_bounds=False,
                constraints=[
                    EqConstraint(
                        f"{process.name}_no_runs",
                        process,
                        run_vector[process.index],
                    )
                ]
                + eq_cons,
                objective=objective,
                maxiter=None,
                allow_inconsistent_order_of_mag=allow_inconsistent_order_of_mag,
            )
            for process in processes
        ],
        dtype=float,
    )
    return np.einsum("ij, kj -> ki", process_process_matrix, production_matrix)


class Solver:
    _resources: Resources
    _processes: Processes
    run_vector: ndarray  # processes
    _resource_matrix: Optional[ndarray]  # (resource, process)
    _flow_matrix: Optional[ndarray]  # (resource, process, process)
    _cumulative_resource_matrix: Optional[ndarray]  # (resource, process)

    def __init__(
        self,
        resources: Resources,
        processes: Processes,
        constraints: Union[
            List[Union[EqConstraint, LeConstraint]],
            List[EqConstraint],
            List[LeConstraint],
        ],
        use_process_bounds: bool,
        objective: Optional[ProcessExpr] = None,
        maxiter: Optional[int] = None,
        allow_inconsistent_order_of_mag: bool = False,
    ):
        self._resources = resources
        self._processes = processes
        self._allow_inconsistent_order_of_mag = allow_inconsistent_order_of_mag
        self.run_vector = solve(
            resources=resources,
            processes=processes,
            use_process_bounds=use_process_bounds,
            constraints=constraints,
            objective=objective,
            maxiter=maxiter,
            allow_inconsistent_order_of_mag=self._allow_inconsistent_order_of_mag,
        )
        self._resource_matrix = None
        self._flow_matrix = None
        self._cumulative_resource_matrix = None

    @property
    def resource_matrix(self):
        if self._resource_matrix is None:
            self._resource_matrix = construct_resource_matrix(
                self._processes.process_produces, self.run_vector
            )
        return self._resource_matrix

    @property
    def flow_matrix(self):
        if self._flow_matrix is None:
            self._flow_matrix = construct_flow_matrix(self.resource_matrix)
        return self._flow_matrix

    @property
    def cumulative_resource_matrix(self):
        if self._cumulative_resource_matrix is None:
            self._cumulative_resource_matrix = (
                construct_cumulative_resource_matrix(
                    self._resources,
                    self._processes,
                    self.run_vector,
                    self._allow_inconsistent_order_of_mag,
                )
            )
        return self._cumulative_resource_matrix


class BoundedSolver(Solver):
    _run_vector_lb: Optional[ndarray]
    _run_vector_ub: Optional[ndarray]
    _resource_matrix_lb: Optional[ndarray]  # (resource, process)
    _resource_matrix_ub: Optional[ndarray]  # (resource, process)
    _flow_matrix_lb: Optional[ndarray]  # (resource, process, process)
    _flow_matrix_ub: Optional[ndarray]  # (resource, process, process)
    _cumulative_resource_matrix: Optional[ndarray]  # (resource, process)
    _solvers: Optional[List[Solver]]

    def __init__(
        self,
        resources: Resources,
        processes: Processes,
        constraints: Union[
            List[Union[EqConstraint, LeConstraint]],
            List[EqConstraint],
            List[LeConstraint],
        ],
        objective: Optional[ProcessExpr] = None,
        maxiter: Optional[int] = None,
        allow_inconsistent_order_of_mag: bool = False,
    ):
        self._resources = resources
        self._processes = processes
        self._allow_inconsistent_order_of_mag = allow_inconsistent_order_of_mag

        self._resource_matrix = None
        self._resource_matrix_lb = None
        self._resource_matrix_ub = None
        self._flow_matrix = None
        self._flow_matrix_lb = None
        self._flow_matrix_ub = None
        self._cumulative_resource_matrix = None
        self._cumulative_resource_matrix_lb = None
        self._cumulative_resource_matrix_ub = None

        self._exact_solver = Solver(
            resources,
            processes,
            constraints,
            use_process_bounds=False,
            objective=objective,
            maxiter=maxiter,
            allow_inconsistent_order_of_mag=self._allow_inconsistent_order_of_mag,
        )
        self.run_vector = self._exact_solver.run_vector
        self._run_vector_lb = None
        self._run_vector_ub = None
        if processes._calculate_bounds:
            solvers = [self._exact_solver]
            for process in processes:
                lower_solver = Solver(
                    resources,
                    processes,
                    constraints,
                    use_process_bounds=True,
                    objective=process * 1,
                    maxiter=maxiter,
                    allow_inconsistent_order_of_mag=self._allow_inconsistent_order_of_mag,
                )
                upper_solver = Solver(
                    resources,
                    processes,
                    constraints,
                    use_process_bounds=True,
                    objective=-process * 1,
                    maxiter=maxiter,
                    allow_inconsistent_order_of_mag=self._allow_inconsistent_order_of_mag,
                )
                solvers.append(lower_solver)
                solvers.append(upper_solver)
            self._solvers = solvers
        else:
            self._solvers = None

    @property
    def run_vector_lb(self):
        if self._solvers is None:
            return self.run_vector
        else:
            if self._run_vector_lb is None:
                self._run_vector_lb = np.min(
                    np.array([i.run_vector for i in self._solvers]), axis=0
                )
            return self._run_vector_lb

    @property
    def run_vector_ub(self):
        if self._solvers is None:
            return self.run_vector
        else:
            if self._run_vector_ub is None:
                self._run_vector_ub = np.max(
                    np.array([i.run_vector for i in self._solvers]), axis=0
                )
            return self._run_vector_ub

    @property
    def resource_matrix(self):
        if self._resource_matrix is None:
            self._resource_matrix = self._exact_solver.resource_matrix
        return self._resource_matrix

    @property
    def resource_matrix_lb(self):
        if self._resource_matrix_lb is None:
            if self._solvers is None:
                self._resource_matrix_lb = self._exact_solver.resource_matrix
            else:
                self._resource_matrix_lb = np.min(
                    np.array([i.resource_matrix for i in self._solvers]),
                    axis=0,
                )
        return self._resource_matrix_lb

    @property
    def resource_matrix_ub(self):
        if self._resource_matrix_ub is None:
            if self._solvers is None:
                self._resource_matrix_ub = self._exact_solver.resource_matrix
            else:
                self._resource_matrix_ub = np.max(
                    np.array([i.resource_matrix for i in self._solvers]),
                    axis=0,
                )
        return self._resource_matrix_ub

    @property
    def flow_matrix(self):
        if self._flow_matrix is None:
            self._flow_matrix = self._exact_solver.flow_matrix
        return self._flow_matrix

    @property
    def flow_matrix_lb(self):
        if self._flow_matrix_lb is None:
            if self._solvers is None:
                self._flow_matrix_lb = self._exact_solver.flow_matrix
            else:
                self._flow_matrix_lb = np.min(
                    np.array([i.flow_matrix for i in self._solvers]),
                    axis=0,
                )
        return self._flow_matrix_lb

    @property
    def flow_matrix_ub(self):
        if self._flow_matrix_ub is None:
            if self._solvers is None:
                self._flow_matrix_ub = self._exact_solver.flow_matrix
            else:
                self._flow_matrix_ub = np.max(
                    np.array([i.flow_matrix for i in self._solvers]),
                    axis=0,
                )
        return self._flow_matrix_ub

    @property
    def cumulative_resource_matrix(self):
        if self._cumulative_resource_matrix is None:
            self._cumulative_resource_matrix = (
                self._exact_solver.cumulative_resource_matrix
            )
        return self._cumulative_resource_matrix

    @property
    def cumulative_resource_matrix_lb(self):
        if self._cumulative_resource_matrix_lb is None:
            if self._solvers is None:
                self._cumulative_resource_matrix_lb = (
                    self._exact_solver.cumulative_resource_matrix
                )
            else:
                self._cumulative_resource_matrix_lb = np.min(
                    np.array(
                        [i.cumulative_resource_matrix for i in self._solvers]
                    ),
                    axis=0,
                )
        return self._cumulative_resource_matrix_lb

    @property
    def cumulative_resource_matrix_ub(self):
        if self._cumulative_resource_matrix_ub is None:
            if self._solvers is None:
                self._cumulative_resource_matrix_ub = (
                    self._exact_solver.cumulative_resource_matrix
                )
            else:
                self._cumulative_resource_matrix_ub = np.max(
                    np.array(
                        [i.cumulative_resource_matrix for i in self._solvers]
                    ),
                    axis=0,
                )
        return self._cumulative_resource_matrix_ub
