import pandas as pd
from Lior_Simulation import Simulation, SimulationSociallyMotivatedEnvironment
from Lior_Simulation import SimulationEgoistsEnvironment, SimulationAltruistsEnvironment
import openpyxl
from Data import Data, SimulationData, AllSimulationData
import copy

final_iteration = 1000


# def save_to_excel(id, data, name):
#     utility_data = pd.DataFrame(data.utility_data)
#     agent_data = pd.DataFrame(data.agent_data)
#     neighbours_data = pd.DataFrame(data.neighbours_data)
#     moral_agent_data = pd.DataFrame(data.moral_agent_data)
#     moral_neighbours_data = pd.DataFrame(data.moral_neighbours_data)
#     global_utility_data = pd.DataFrame(data.global_utility_data)
#     any_time_data = pd.DataFrame(data.any_time_data)
#     xlName = str(name) + str(id) + ".xlsx"
#     xlwriter = pd.ExcelWriter(xlName)
#     utility_data.to_excel(xlwriter, sheet_name='utilities')
#     agent_data.to_excel(xlwriter, sheet_name='agents', index=False)
#     neighbours_data.to_excel(xlwriter, sheet_name='neighbours', index=False)
#     moral_agent_data.to_excel(xlwriter, sheet_name='ME agent', index=False)
#     moral_neighbours_data.to_excel(xlwriter, sheet_name='ME neighbours', index=False)
#     global_utility_data.to_excel(xlwriter, sheet_name='Global Utility', index=False)
#     any_time_data.to_excel(xlwriter, sheet_name='Any Time', index=False)
#     xlwriter.close()
#
#
# def simulation_save_to_excel(id, sim):
#     simulation_data = pd.DataFrame(sim.simulation_data)
#     xlName = "Simulation" + str(id) + ".xlsx"
#     xlwriter = pd.ExcelWriter(xlName)
#     simulation_data.to_excel(xlwriter, sheet_name='simulation analysis', index=False)
#     xlwriter.close()


def analysis_save_to_excel(sim, environmentType):
    line_chart_personal_data = pd.DataFrame(sim.line_chart_personal_mean_data)
    line_chart_neighbors_data = pd.DataFrame(sim.line_chart_neighbors_mean_data)
    line_chart_global_data = pd.DataFrame(sim.line_chart_global_mean_data)
    impact_utility_coordinates_data = pd.DataFrame(sim.impact_utility_coordinates_data)
    xlName = environmentType + "Simulation.xlsx"
    xlwriter = pd.ExcelWriter(xlName)
    line_chart_personal_data.to_excel(xlwriter, sheet_name='personal data analysis')
    line_chart_neighbors_data.to_excel(xlwriter, sheet_name='neighbors data analysis')
    line_chart_global_data.to_excel(xlwriter, sheet_name='global data analysis')
    impact_utility_coordinates_data.to_excel(xlwriter, sheet_name='impact utility data analysis')
    xlwriter.close()


# ----------------------------------------------------------------------------------------------------------
def neighbours2agent(neighbours, agents, agent_id):
    send = {}
    # neighbours_id is list of neighbours id
    neighbours_id = neighbours[agent_id]
    for neighbour_id in neighbours_id:
        # { key: id, value: neighbour}
        send[neighbour_id] = agents[neighbour_id]
    return send


def constraints2agent(constraints, agent_id):
    return constraints[agent_id]


def get_agent(agents, agent_id):
    return agents[agent_id]


# ----------------------------------------------------------------------------------------------------------
def simulation_one_special_run(id, simulation_data, agent_type, agent0, agents, neighbours, constraints):
    data = Data()  # save data here
    agents[0] = agent0  # replace with special agent
    data.set_neighbours_data(neighbours)  # update data - save connections
    for agent_id in agents.keys():
        # for every agent - initiate
        a_neighbours = neighbours2agent(neighbours, agents, agent_id)
        a_constraints = constraints2agent(constraints, agent_id)
        agent = get_agent(agents, agent_id)
        agent.initiate(a_neighbours, a_constraints)
    # start running the algorithm
    i = 0
    while i < final_iteration:
        up = False
        for agent_id in agents.keys():
            agent = get_agent(agents, agent_id)
            agent.listen()
        for agent_id in agents.keys():
            agent = get_agent(agents, agent_id)
            if agent.phase == 4:
                data.update_data(agent.get_data())  # save data here
                up = True
            agent.reply()
        if up:
            i = i + 1
    data.update_best_iteration_data()
    # save_to_excel(id, data, "Simulation"+agent_type )
    simulation_data.update_data(data, agent_type)


# _________________________________________________________________________________________________________________
# _________________________________________________________________________________________________________________
def simulation_egoists_environment(id):
    s = SimulationEgoistsEnvironment(id, 50, 10, 35)
    # --------------------------------------------same seed
    agents = s.create_agents()
    neighbours = s.create_connections()
    constraints = s.create_constraints()
    # --------------------------------------------special agents
    egoist = s.create_egoist_agent()
    altruist = s.create_altruist_agent()
    simple = s.create_simple_agent()
    careful = s.create_careful_agent()
    generous = s.create_generous_agent()
    selfish = s.create_selfish_agent()
    random = s.create_random_agent()
    # --------------------------------------------DATA
    simulation_data = SimulationData()
    # --------------------------------------------RUN
    simulation_one_special_run(id, simulation_data, "Simple", simple, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Careful", careful, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Generous", generous, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Selfish", selfish, copy.deepcopy(agents),
                               copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Random", random, copy.deepcopy(agents), copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Altruist", altruist, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Egoist", egoist, copy.deepcopy(agents), copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    # --------------------------------------------Analysis
    # simulation_save_to_excel(id, simulation_data)
    print("id:", id)
    return simulation_data


# _________________________________________________________________________________________________________________
def simulation_altruists_environment(id):
    s = SimulationAltruistsEnvironment(id, 50, 10, 35)
    # --------------------------------------------same seed
    agents = s.create_agents()
    neighbours = s.create_connections()
    constraints = s.create_constraints()
    # --------------------------------------------special agents
    egoist = s.create_egoist_agent()
    altruist = s.create_altruist_agent()
    simple = s.create_simple_agent()
    careful = s.create_careful_agent()
    generous = s.create_generous_agent()
    selfish = s.create_selfish_agent()
    random = s.create_random_agent()
    # --------------------------------------------DATA
    simulation_data = SimulationData()
    # --------------------------------------------RUN
    simulation_one_special_run(id, simulation_data, "Simple", simple, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Careful", careful, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Generous", generous, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Selfish", selfish, copy.deepcopy(agents),
                               copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Random", random, copy.deepcopy(agents), copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Altruist", altruist, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Egoist", egoist, copy.deepcopy(agents), copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    # --------------------------------------------Analysis
    # simulation_save_to_excel(id, simulation_data)
    print("id:", id)
    return simulation_data


# _________________________________________________________________________________________________________________
def simulation_socially_motivated_environment(id):
    s = SimulationSociallyMotivatedEnvironment(id, 50, 10, 10)
    # --------------------------------------------same seed
    agents = s.create_agents()
    neighbours = s.create_connections()
    constraints = s.create_constraints()
    # --------------------------------------------ME agents
    simple = s.create_simple_agent()
    careful = s.create_careful_agent()
    generous = s.create_generous_agent()
    selfish = s.create_selfish_agent()
    random = s.create_random_agent()
    egoist = s.create_egoist_agent()
    altruist = s.create_altruist_agent()
    # --------------------------------------------DATA
    simulation_data = SimulationData()
    # --------------------------------------------RUN
    simulation_one_special_run(id, simulation_data, "Simple", simple, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Careful", careful, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Generous", generous, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Selfish", selfish, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Random", random, copy.deepcopy(agents), copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Egoist", egoist, copy.deepcopy(agents), copy.deepcopy(neighbours),
                               copy.deepcopy(constraints))
    simulation_one_special_run(id, simulation_data, "Altruist", altruist, copy.deepcopy(agents),
                               copy.deepcopy(neighbours), copy.deepcopy(constraints))

    # --------------------------------------------Analysis
    # simulation_save_to_excel(id, simulation_data)
    print("id:", id)
    return simulation_data


# _________________________________________________________________________________________________________________
# ******************************************************************************************************
def run_simulations_sm_environment(how_many):
    sim_data = []
    for index in range(0, how_many):
        sim_data.append(simulation_socially_motivated_environment(index))
    all_simulation_data_analysis = AllSimulationData(sim_data)
    all_simulation_data_analysis.update_data()
    analysis_save_to_excel(all_simulation_data_analysis, "SM_")


def run_simulations_altru_environment(how_many):
    sim_data = []
    for index in range(0, how_many):
        sim_data.append(simulation_altruists_environment(index))
    all_simulation_data_analysis = AllSimulationData(sim_data)
    all_simulation_data_analysis.update_data()
    analysis_save_to_excel(all_simulation_data_analysis, "A_")


def run_simulations_ego_environment(how_many):
    sim_data = []
    for index in range(0, how_many):
        sim_data.append(simulation_egoists_environment(index))
    all_simulation_data_analysis = AllSimulationData(sim_data)
    all_simulation_data_analysis.update_data()
    analysis_save_to_excel(all_simulation_data_analysis, "E_")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # run_simulations_sm_environment(1)
#     run_simulations_altru_environment(100)
    run_simulations_ego_environment(100)
