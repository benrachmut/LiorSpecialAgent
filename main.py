from enums import Algorithm

if __name__ == '__main__':
    dcop_type = DcopType.graph_coloring
    algorithm = Algorithm.branch_and_bound
    dcops = []
    for i in range(repetitions):
        dcops.append(create_selected_dcop(i,dcop_type,algorithm))
    solve_dcops(dcops)
    #create_data(dcops)

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