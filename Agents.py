import math

from Message import Message
import numpy as np
import random


class Agent:
    # neighbours - list of agent Ai’s neighbours { key: id, value: neighbour}
    # constraints - set of agent Ai’s constraint matrixes with his neighbours { key: neighbour_id, value: matrix}
    def __init__(self, id, domainSize, privacyLevel):
        self.id = id
        self.domainSize = domainSize
        self.privacyLevel = privacyLevel
        self.assignment = 0
        self.utility = 0
        # -------------------initialise phase
        self.neighbours = {}
        self.constraints = {}
        self.domain = []
        # -------------------information
        self.alterValue = 0
        self.my_local_change = 0
        self.offered_local_changes = []
        self.LocalView = {}
        self.taboos = {}  # my taboos
        # -------------------messages
        self.message_box = []
        # -------------------data
        self.phase = 0
        self.iteration = 0
        self.totalIterations = 1000

    # __________________________________________________________________initiate:
    # neighbours - { key: id, value: neighbour}
    def init_neighbours(self, neighbours):
        self.neighbours = neighbours

    # constraints - { key: neighbour id, value: matrix}
    def init_constraints(self, constraints):
        self.constraints = constraints

    # by domain size
    def init_domain(self):
        for i in range(self.domainSize):
            self.domain.append(i)

    # _____________________________________________________________________________PRIVET METHODS:
    # _______________________________________________________________message_boxes:
    # ------------clear
    # PHASE 1 - value
    # PHASE 2 - pref
    # PHASE 3 - alternative_value_and_improvement
    # PHASE 4 - taboo
    def clear_message_box(self):
        self.message_box = []

    # ------------collect
    # PHASE 1 - value
    # PHASE 2 - pref
    # PHASE 3 - alternative_value_and_improvement
    # PHASE 4 - taboo
    def collect_messages(self, msg):
        self.message_box.append(msg)

    # ------------send
    # PHASE 1 - pref
    # PHASE 2 - alternative_value_and_improvement
    # PHASE 3 - taboo
    # PHASE 4 - value
    def send_messages(self, messages_to_send):
        # messages_to_send = {key: neighbour_id, value: msg}
        for neighbour_id in messages_to_send:
            neighbour = self.neighbours[neighbour_id]
            msg = messages_to_send[neighbour_id]
            neighbour.collect_messages(msg)

    # ------------make
    # PHASE 1 - pref
    def make_pref_messages(self):
        messages_to_send = {}
        if self.privacyLevel == 2:
            pass
        elif self.privacyLevel == 3:
            pass
        else:
            for neighbour_id in self.neighbours:
                pref_list = self.privacy_level_1_full_information(neighbour_id)
                content = pref_list
                sender = self.id
                receiver = neighbour_id
                msg = Message(sender, receiver, content)
                messages_to_send[neighbour_id] = msg
        return messages_to_send

    # PHASE 2 - alternative_value_and_improvement
    # def make_alternative_value_and_improvement_messages(self, indications):
    #     socialGain = self.calculate_social_gain_for_alter_value(indications)
    #     messages_to_send = {}
    #     content = [self.alterValue, socialGain]
    #     sender = self.id
    #     for neighbour_id in self.neighbours:
    #         receiver = neighbour_id
    #         msg = Message(sender, receiver, content)
    #         messages_to_send[neighbour_id] = msg
    #     return messages_to_send

    # PHASE 2 - alternative_value
    def make_alternative_value_local_change_messages(self):
        messages_to_send = {}
        content = [self.alterValue, self.my_local_change]
        sender = self.id
        for neighbour_id in self.neighbours:
            receiver = neighbour_id
            msg = Message(sender, receiver, content)
            messages_to_send[neighbour_id] = msg
        return messages_to_send

    # PHASE 3 - taboo
    def make_taboo_messages(self):
        # send taboo if passed the threshold
        # send smaller_social_gain if my improvement is better than the neighbour's
        pass

    # PHASE 4 - value
    def make_value_messages(self):
        messages_to_send = {}
        content = self.assignment
        sender = self.id
        for neighbour_id in self.neighbours:
            receiver = neighbour_id
            msg = Message(sender, receiver, content)
            messages_to_send[neighbour_id] = msg
        return messages_to_send

    # _______________________________________________________________calculate:
    # ----------------------------PHASE 1 - pref messages
    # potential change in utility for each assignment in the domain
    def privacy_level_1_full_information(self, neighbour_id):
        indications_list = np.zeros(self.domainSize, dtype=int)
        constraint_matrix_with_n = self.constraints[neighbour_id]
        # find permanent part of utility
        perm_uti = self.only_one_change_assignment(neighbour_id)
        for index in range(len(indications_list)):
            potential_utility = perm_uti + constraint_matrix_with_n[self.assignment][index]
            indications_list[index] = potential_utility - self.utility
        return indications_list

    # (potential change in utility/ total utility) for each assignment in the domain
    def privacy_level_2_relative_information(self, neighbour_id):  # *************************** fix!!!
        indications_matrix = np.zeros((self.domainSize, self.domainSize))
        constraint_matrix_with_n = self.constraints[neighbour_id]
        for row in indications_matrix:
            for column in row:
                potential_utility = constraint_matrix_with_n[row][column]
                indications_matrix[row][column] = (potential_utility - self.utility) / self.utility
        return indications_matrix

    # which assignment in the neighbor’s’ domain of is the most preferable to me, and by how much (potential change in utility)
    def privacy_level_3_preferences(self, neighbour):
        pass

    # ----------------------------calculate utility:
    def calculate_utility(self, assignment):
        utility = 0
        for neighbour_id in self.neighbours:
            # column for constraint matrix
            neighbour_assignment = self.LocalView[neighbour_id]
            constraint_matrix_with_n = self.constraints[neighbour_id]
            uti = constraint_matrix_with_n[assignment][neighbour_assignment]
            utility = utility + uti
        return utility

    # ----------------------------calculate social gain for alter value:
    def calculate_local_change_for_alter_value(self, indications):
        my_change = self.calculate_utility(self.alterValue) - self.utility
        n_local_change = 0
        for neighbour_id in self.neighbours:
            # local changes for neighbours:
            indications_list_from_n = indications[neighbour_id]
            n_change = indications_list_from_n[self.alterValue]
            n_local_change = n_local_change + n_change
        self.my_local_change = my_change + n_local_change

    # ----------------------------calculate perm uti:
    def only_one_change_assignment(self, neighbour_id):
        # perm uti = utility - relative utility of this neighbour
        # potential_utility = perm uti + utility per assignment of neighbour
        # indications = potential_utility - current utilitys
        constraint_matrix_with_n = self.constraints[neighbour_id]
        # find permanent part of utility
        neighbour_assignment = self.LocalView[neighbour_id]
        perm_uti = self.utility - constraint_matrix_with_n[self.assignment][neighbour_assignment]
        return perm_uti

    def __str__(self):
        s = "agent ID: " + str(self.id) + ", utility: " + str(self.utility)
        return s
class AltruistAgent(Agent):
    def __init__(self, id, domainSize, privacyLevel=1):
        Agent.__init__(self, id, domainSize, privacyLevel)

    def __str__(self):
        s = "I am a Fully Altruist agent, ID: " + str(self.id) + ", utility: " + str(self.utility)
        return s

    # DATA
    def get_data(self):
        # Iteration, Assignment, Utility, None, None, None
        data = [self.iteration, self.id, self.assignment, self.utility, 0, 0, 0, 0, 0]
        return data

    # _____________________________________________________________________________PRIVET METHODS:
    # PHASE 2
    def calculate_next_assignment(self, indications):
        criterion = -math.inf
        next_assignment = self.assignment
        for assignment in range(self.domainSize):
            social_gain = 0
            for neighbour_id in self.neighbours:
                # local changes for neighbours
                indications_list_from_n = indications[neighbour_id]
                n_gain = indications_list_from_n[assignment]
                social_gain = social_gain + n_gain
            if social_gain > criterion:
                criterion = social_gain
                next_assignment = assignment
        if criterion > 0:
            self.alterValue = next_assignment
        elif (self.iteration/1000) > random.uniform(0, 1):
            self.alterValue = self.assignment
        else:
            self.alterValue = random.randint(0, 9)

    # PHASE 4
    def change_assignment(self):
        self.assignment = self.alterValue

    # _____________________________________________________________________________ALGORITHM:

    def listen(self):
        if self.phase == 1:
            self.listen_phase_1()
        elif self.phase == 2:
            self.listen_phase_2()
        elif self.phase == 3:
            self.listen_phase_3()
        elif self.phase == 4:
            self.listen_phase_4()

    def reply(self):
        if self.phase == 1:
            self.reply_phase_1()
        elif self.phase == 2:
            self.reply_phase_2()
        elif self.phase == 3:
            self.reply_phase_3()
        elif self.phase == 4:
            self.reply_phase_4()

        # ______________________________________initiate:

    def initiate(self, neighbours, constraints):
        self.init_neighbours(neighbours)
        self.init_constraints(constraints)
        self.init_domain()
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        self.phase = 1

        # ________________________________________________________PHASE 1

    def listen_phase_1(self):
        # update local view
        for msg in self.message_box:
            self.LocalView[msg.get_sender()] = msg.get_content()  # content = neighbor's assignment
        self.clear_message_box()
        # update utility
        self.utility = self.calculate_utility(self.assignment)

    def reply_phase_1(self):
        # send preferences to all neighbors
        messages_to_send = self.make_pref_messages()
        self.send_messages(messages_to_send)
        self.phase = 2

        # ________________________________________________________PHASE 2

    def listen_phase_2(self):
        # update indications
        indications = {}
        for msg in self.message_box:
            indications[msg.get_sender()] = msg.get_content()  # content = neighbor's list pref
        self.clear_message_box()
        # look for next assignment
        self.calculate_next_assignment(indications)
        self.calculate_local_change_for_alter_value(indications)

    def reply_phase_2(self):
        # send local changes and alter_value to all neighbors
        messages_to_send = self.make_alternative_value_local_change_messages()
        self.send_messages(messages_to_send)
        self.phase = 3

        # ________________________________________________________PHASE 3

    def listen_phase_3(self):
        # update local changes
        self.offered_local_changes = []
        for msg in self.message_box:
            self.offered_local_changes.append(msg.get_content()[1])  # content = neighbor's local change
        self.clear_message_box()
        # no threshold

    def reply_phase_3(self):
        # send empty taboo to all neighbors
        self.send_messages(self.taboos)
        self.phase = 4

        # ________________________________________________________PHASE 4

    def listen_phase_4(self):  # not monotony
        # no need to update taboo messages
        self.clear_message_box()
        if self.my_local_change > -((1000 - self.iteration) / 10):
            if self.assignment != self.alterValue:
                self.change_assignment()

    def reply_phase_4(self):
        # send value messages
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        # finish iteration
        self.iteration = self.iteration + 1
        self.phase = 1
class EgoistAgent(Agent):
    def __init__(self, id, domainSize, privacyLevel=1):
        Agent.__init__(self, id, domainSize, privacyLevel)

    def __str__(self):
        s = "I am a Fully Egoist agent, ID: " + str(self.id) + ", utility: " + str(self.utility)
        return s

    # DATA
    def get_data(self):
        # Iteration, Assignment, Utility, None, None, None
        data = [self.iteration, self.id, self.assignment, self.utility, 0, 0, 0, 0, 0]
        return data

    # _____________________________________________________________________________PRIVET METHODS:
    # PHASE 2
    def calculate_next_assignment(self):
        criterion = -math.inf
        next_assignment = self.assignment
        for assignment in range(self.domainSize):
            utility = self.calculate_utility(assignment)
            if utility > criterion:
                criterion = utility
                next_assignment = assignment
        if criterion > 0:
            self.alterValue = next_assignment
        elif (self.iteration/1000) > random.uniform(0, 1):
            self.alterValue = self.assignment
        else:
            self.alterValue = random.randint(0, 9)

    # PHASE 4
    def change_assignment(self):
        self.assignment = self.alterValue

    # _____________________________________________________________________________ALGORITHM:

    def listen(self):
        if self.phase == 1:
            self.listen_phase_1()
        elif self.phase == 2:
            self.listen_phase_2()
        elif self.phase == 3:
            self.listen_phase_3()
        elif self.phase == 4:
            self.listen_phase_4()

    def reply(self):
        if self.phase == 1:
            self.reply_phase_1()
        elif self.phase == 2:
            self.reply_phase_2()
        elif self.phase == 3:
            self.reply_phase_3()
        elif self.phase == 4:
            self.reply_phase_4()

        # ______________________________________initiate:

    def initiate(self, neighbours, constraints):
        self.init_neighbours(neighbours)
        self.init_constraints(constraints)
        self.init_domain()
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        self.phase = 1

    # ________________________________________________________PHASE 1

    def listen_phase_1(self):
        # update local view
        for msg in self.message_box:
            self.LocalView[msg.get_sender()] = msg.get_content()  # content = neighbor's assignment
        self.clear_message_box()
        # update utility
        self.utility = self.calculate_utility(self.assignment)

    def reply_phase_1(self):
        # send preferences to all neighbors
        messages_to_send = self.make_pref_messages()
        self.send_messages(messages_to_send)
        self.phase = 2

    # ________________________________________________________PHASE 2

    def listen_phase_2(self):
        # update indications
        indications = {}
        for msg in self.message_box:
            indications[msg.get_sender()] = msg.get_content()  # content = neighbor's list pref
        self.clear_message_box()
        # look for next assignment
        self.calculate_next_assignment()
        self.calculate_local_change_for_alter_value(indications)

    def reply_phase_2(self):
        # send local changes and alter_value to all neighbors
        messages_to_send = self.make_alternative_value_local_change_messages()
        self.send_messages(messages_to_send)
        self.phase = 3

    # ________________________________________________________PHASE 3

    def listen_phase_3(self):
        # update local changes
        self.offered_local_changes = []
        for msg in self.message_box:
            self.offered_local_changes.append(msg.get_content()[1])  # content = neighbor's local change
        self.clear_message_box()
        # no threshold

    def reply_phase_3(self):
        # send empty taboo to all neighbors
        self.send_messages(self.taboos)
        self.phase = 4

    # ________________________________________________________PHASE 4

    def listen_phase_4(self):  # not monotony
        # no need to update taboo messages
        self.clear_message_box()
        if self.my_local_change > -((1000 - self.iteration) / 10):
            if self.assignment != self.alterValue:
                self.change_assignment()

    def reply_phase_4(self):
        # send value messages
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        # finish iteration
        self.iteration = self.iteration + 1
        self.phase = 1
class SMagent(Agent):
    def __init__(self, id, domainSize, bound, privacyLevel=1):
        Agent.__init__(self, id, domainSize, privacyLevel)
        self.baseLine = 0
        self.bound = bound

    def __str__(self):
        s = "I am a Socially Motivated agent, ID: " + str(self.id) + ", utility: " + str(self.utility) + ", baseLine: " \
            + str(self.baseLine) + ", bound:  " + str(self.bound)
        return s

    # DATA
    def get_data(self):
        # Iteration, Assignment, Utility, None, baseLine, bound
        data = [self.iteration, self.id, self.assignment, self.utility, None, None, None, self.baseLine, self.bound]
        return data

    # _____________________________________________________________________________PRIVET METHODS:
    # PHASE 1
    def update_base_line(self):
        base_line = (self.baseLine + self.utility) / 2
        self.baseLine = base_line

    # PHASE 2
    def calculate_next_assignment(self, indications):
        vote_list = [0] * self.domainSize
        gain_list = [0] * self.domainSize
        # __________________________________________neighbours pref
        for neighbour_id in self.neighbours:
            pref_list = indications[neighbour_id]  # assignment num
            for option in range(len(pref_list)):
                gain_list[option] = gain_list[option] + pref_list[option]
            vote = np.argmax(pref_list)
            vote_list[vote] = vote_list[vote] + 1
        # __________________________________________my pref
        criterion = -math.inf
        my_pref = self.assignment
        for assignment in range(self.domainSize):
            utility = self.calculate_utility(assignment)
            gain_list[assignment] = gain_list[assignment] + utility
            if utility > criterion:
                criterion = utility
                my_pref = assignment
        vote_list[my_pref] = vote_list[my_pref] + 1
        # __________________________________________analyze
        probability_list = np.array(vote_list) / (len(self.neighbours) + 1)
        expectation_list = probability_list * np.array(gain_list)
        alter = random.choices(self.domain, expectation_list)[0]
        self.alterValue = alter

    # PHASE 3
    def calculate_threshold(self, alternative_values):
        self.taboos = {}
        for neighbour_id in alternative_values:
            neighbour_alter_value = alternative_values[neighbour_id]
            perm_uti = self.only_one_change_assignment(neighbour_id)
            constraint_matrix_with_n = self.constraints[neighbour_id]
            new_uti = constraint_matrix_with_n[self.assignment][neighbour_alter_value]
            potential_utility = perm_uti + new_uti
            # print(self.id, potential_utility, self.baseLine , self.baseLine - self.baseLine * self.bound)
            if potential_utility < (self.baseLine - self.baseLine * self.bound):
                content = neighbour_alter_value
                sender = self.id
                receiver = neighbour_id
                msg = Message(sender, receiver, content)
                self.taboos[neighbour_id] = msg

    # PHASE 4
    def change_assignment(self):
        self.assignment = self.alterValue

    # _____________________________________________________________________________ALGORITHM:

    def listen(self):
        if self.phase == 1:
            self.listen_phase_1()
        elif self.phase == 2:
            self.listen_phase_2()
        elif self.phase == 3:
            self.listen_phase_3()
        elif self.phase == 4:
            self.listen_phase_4()

    def reply(self):
        if self.phase == 1:
            self.reply_phase_1()
        elif self.phase == 2:
            self.reply_phase_2()
        elif self.phase == 3:
            self.reply_phase_3()
        elif self.phase == 4:
            self.reply_phase_4()

        # ______________________________________initiate:

    def initiate(self, neighbours, constraints):
        self.init_neighbours(neighbours)
        self.init_constraints(constraints)
        self.init_domain()
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        self.phase = 1

        # ________________________________________________________PHASE 1

    def listen_phase_1(self):
        # update local view
        for msg in self.message_box:
            self.LocalView[msg.get_sender()] = msg.get_content()  # content = neighbor's assignment
        self.clear_message_box()
        # update utility
        self.utility = self.calculate_utility(self.assignment)
        self.update_base_line()

    def reply_phase_1(self):
        # send preferences to all neighbors
        messages_to_send = self.make_pref_messages()
        self.send_messages(messages_to_send)
        self.phase = 2

        # ________________________________________________________PHASE 2

    def listen_phase_2(self):
        # update indications
        indications = {}
        for msg in self.message_box:
            indications[msg.get_sender()] = msg.get_content()  # content = neighbor's list pref
        self.clear_message_box()
        # look for next assignment
        self.calculate_next_assignment(indications)
        self.calculate_local_change_for_alter_value(indications)

    def reply_phase_2(self):
        # send local changes and alter_value to all neighbors
        messages_to_send = self.make_alternative_value_local_change_messages()
        self.send_messages(messages_to_send)
        self.phase = 3

        # ________________________________________________________PHASE 3

    def listen_phase_3(self):
        # update alternative values and local changes
        alternative_values = {}
        self.offered_local_changes = []
        for msg in self.message_box:
            alternative_values[msg.get_sender()] = msg.get_content()[0]  # content = neighbor's alter val
            self.offered_local_changes.append(msg.get_content()[1])  # content = neighbor's local change
        self.clear_message_box()
        # check threshold
        self.calculate_threshold(alternative_values)  # { key: neighbour_id, value: taboo}

    def reply_phase_3(self):
        # send taboo to all neighbors
        self.send_messages(self.taboos)
        self.phase = 4

        # ________________________________________________________PHASE 4

    def listen_phase_4(self):  # not monotony
        # update taboo messages
        taboos = {}
        for msg in self.message_box:
            taboos[msg.get_sender()] = msg.get_content()  # content = taboo
        self.clear_message_box()
        # check limitations
        if not taboos:  # if no taboos
            if self.my_local_change > 0:
                if self.assignment != self.alterValue:
                    self.change_assignment()


    def reply_phase_4(self):
        # send value messages
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        # finish iteration
        self.iteration = self.iteration + 1
        self.phase = 1

    # ----------------------------MGM can change value:
    def can_change_value_mgm(self):
        self.offered_local_changes.append(self.my_local_change)
        # if (self.iteration/self.totalIterations) < random.uniform(0, 1):
        #     self.offered_local_changes = [i for i in self.offered_local_changes if i != 0]
        if self.offered_local_changes:
            if self.my_local_change == max(self.offered_local_changes):  # do not check multiple equals max
                return True
        return False


class MoralAgent(Agent):
    def __init__(self, id, domainSize, privacyLevel=1):
        Agent.__init__(self, id, domainSize, privacyLevel)
        self.cumulative_environmental_impact = 0
        self.possible_EI = {}  # {key: assignment, value: environmental-impact}
        self.expected_impact = 0  # by strategy -if no neighbor change
        self.expected_change_utility = 0  # by strategy -if no neighbor change

    # DATA
    def get_data(self):
        # Iteration, Assignment, Utility, Moral Equilibrium
        data = [self.iteration, self.id, self.assignment, self.utility, self.expected_change_utility,
                self.cumulative_environmental_impact, self.expected_impact, None, None]
        return data

    # _____________________________________________________________________________ALGORITHM:

    def listen(self):
        if self.phase == 1:
            self.listen_phase_1()
        elif self.phase == 2:
            self.listen_phase_2()
        elif self.phase == 3:
            self.listen_phase_3()
        elif self.phase == 4:
            self.listen_phase_4()

    def reply(self):
        if self.phase == 1:
            self.reply_phase_1()
        elif self.phase == 2:
            self.reply_phase_2()
        elif self.phase == 3:
            self.reply_phase_3()
        elif self.phase == 4:
            self.reply_phase_4()

    # ______________________________________initiate:
    def initiate(self, neighbours, constraints):
        self.init_neighbours(neighbours)
        self.init_constraints(constraints)
        self.init_domain()
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        self.phase = 1

    # ________________________________________________________PHASE 1
    def listen_phase_1(self):
        # update local view
        for msg in self.message_box:
            self.LocalView[msg.get_sender()] = msg.get_content()  # content = neighbor's assignment
        self.clear_message_box()
        # update utility
        self.utility = self.calculate_utility(self.assignment)

    def reply_phase_1(self):
        # send preferences to all neighbors
        messages_to_send = self.make_pref_messages()
        self.send_messages(messages_to_send)
        self.phase = 2

    # ________________________________________________________PHASE 2
    def listen_phase_2(self):
        # update indications
        indications = {}
        for msg in self.message_box:
            indications[msg.get_sender()] = msg.get_content()  # content = neighbor's list pref
        self.clear_message_box()
        # look for next assignment
        self.calculate_next_assignment(indications)
        self.calculate_local_change_for_alter_value(indications)
        self.expected_change_utility = self.calculate_utility(self.alterValue) - self.utility

    def reply_phase_2(self):
        # send local changes and alter_value to all neighbors
        messages_to_send = self.make_alternative_value_local_change_messages()
        self.send_messages(messages_to_send)
        self.phase = 3

    # ________________________________________________________PHASE 3
    def listen_phase_3(self):
        # update alternative values
        alternative_values = {}
        self.offered_local_changes = []
        for msg in self.message_box:
            alternative_values[msg.get_sender()] = msg.get_content()[0]  # content = neighbor's alter val
            self.offered_local_changes.append(msg.get_content()[1])  # content = neighbor's local change
        self.clear_message_box()
        # check threshold
        self.calculate_threshold(alternative_values)  # { key: neighbour_id, value: taboo}

    def reply_phase_3(self):
        # send taboo to all neighbors
        self.send_messages(self.taboos)
        self.phase = 4

    # ________________________________________________________PHASE 4
    def listen_phase_4(self):  # not monotony
        # update taboo messages
        taboos = {}
        for msg in self.message_box:
            taboos[msg.get_sender()] = msg.get_content()  # content = taboo
        self.clear_message_box()
        # check limitations
        # if not taboos:  # if no taboos
        if self.assignment != self.alterValue:
            self.change_assignment()
        self.update_cumulative_environmental_impact()

    def reply_phase_4(self):
        # send value messages
        messages_to_send = self.make_value_messages()
        self.send_messages(messages_to_send)
        # finish iteration
        self.iteration = self.iteration + 1
        self.phase = 1

    # _____________________________________________________________________________PRIVET METHODS:
    # ----------------------------calculate alter value:
    # according to my ME - Debits or Credits (Moral Compensation or Moral Licensing)
    def calculate_next_assignment(self, indications):
        if self.cumulative_environmental_impact >= 0:
            self.strategy_moral_licensing(indications)
        else:
            self.strategy_moral_compensation(indications)

    def beneficial_to_myself(self, indications):
        # for every assignment in the domain - improvement for me + local changes for neighbours
        # dictionary[assignment] = [improvement for me, local changes for neighbours]
        beneficial_to_me = {}
        self.possible_EI = {}
        for assignment in range(self.domainSize):
            utility = self.calculate_utility(assignment)
            social_gain = 0
            for neighbour_id in self.neighbours:
                # local changes for neighbours
                indications_list_from_n = indications[neighbour_id]
                n_gain = indications_list_from_n[assignment]
                social_gain = social_gain + n_gain
            improvement_for_me = utility - self.utility
            local_changes = social_gain
            self.possible_EI[assignment] = local_changes
            # groups:
            if improvement_for_me >= 0:
                beneficial_to_me[assignment] = [improvement_for_me, local_changes]
        return beneficial_to_me

    def neighbours_preferences(self, indications):
        # for every assignment in the domain - improvement for me + local changes for neighbours
        # dictionary[assignment] = [improvement for me, local changes for neighbours]
        neighbours_preferences = {}
        self.possible_EI = {}
        for assignment in range(self.domainSize):
            utility = self.calculate_utility(assignment)
            social_gain = 0
            for neighbour_id in self.neighbours:
                # local changes for neighbours
                indications_list_from_n = indications[neighbour_id]
                n_gain = indications_list_from_n[assignment]
                social_gain = social_gain + n_gain
            improvement_for_me = utility - self.utility
            local_changes = social_gain
            self.possible_EI[assignment] = local_changes
            # groups:
            if local_changes >= 0:
                neighbours_preferences[assignment] = [improvement_for_me, local_changes]
        return neighbours_preferences

    # ----------------------------calculate threshold:
    def calculate_threshold(self, alternative_values):
        # return taboo_per_n # { key: neighbour_id, value: taboo}
        start_temp = self.totalIterations
        self.taboos = {}
        for neighbour_id in alternative_values:
            perm_uti = self.only_one_change_assignment(neighbour_id)
            neighbour_alter_value = alternative_values[neighbour_id]
            constraint_matrix_with_n = self.constraints[neighbour_id]
            new_add = constraint_matrix_with_n[self.assignment][neighbour_alter_value]
            potential_utility = perm_uti + new_add
            # difference between candidate and current point evaluation
            diff = potential_utility - self.utility
            if diff < 0:
                # calculate temperature for current iteration, t->0: small percentage, t->inf:  big percentage
                temperature = start_temp - self.iteration
                # calculate metropolis acceptance criterion
                metropolis = math.exp(diff / temperature)
                # it is less likely to add taboo at the beginning of the algorithm (big temp) and if the diff is not big
                if (potential_utility / self.utility) > metropolis:
                    content = neighbour_alter_value
                    sender = self.id
                    receiver = neighbour_id
                    msg = Message(sender, receiver, content)
                    self.taboos[neighbour_id] = msg

    # PHASE 4
    def change_assignment(self):
        self.assignment = self.alterValue

    # PHASE 4
    def update_cumulative_environmental_impact(self):
        self.cumulative_environmental_impact += self.possible_EI[self.assignment]
        self.expected_impact = self.possible_EI[self.assignment]
# moral licensing -> +
# moral compensation -> -
# dictionary[assignment] = [improvement for me, local changes for neighbours]

# _______________________________________________________________________________________________________________
class SimpleAgent(MoralAgent):

    # PHASE 2 - Debits - Choose the option that is most beneficial for the society
    def strategy_moral_compensation(self, indications):
        neighbours_preferences = self.neighbours_preferences(indications)
        if neighbours_preferences:  # not empty
            criterion = -math.inf
            for assignment in neighbours_preferences:
                social_gain = neighbours_preferences[assignment][1]
                if social_gain > criterion:
                    criterion = social_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    # PHASE 2 - Credits - Choose the option that is most beneficial to him
    def strategy_moral_licensing(self, indications):
        beneficial_to_me = self.beneficial_to_myself(indications)
        if beneficial_to_me:  # not empty
            criterion = -math.inf
            for assignment in beneficial_to_me:
                my_gain = beneficial_to_me[assignment][0]
                if my_gain > criterion:
                    criterion = my_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    def __str__(self):
        s = "Simple, utility: " + str(round(self.utility)) + ", EI: " + str(self.cumulative_environmental_impact) + \
            ", assignment: " + str(self.assignment)
        return s


# _______________________________________________________________________________________________________________
class CarefulAgent(MoralAgent):

    # PHASE 2 - Debits - from the neighbours’ preferences
    # choose the option that will least distance him from the balance
    def strategy_moral_compensation(self, indications):
        neighbours_preferences = self.neighbours_preferences(indications)
        if neighbours_preferences:  # not empty
            criterion = math.inf
            for assignment in neighbours_preferences:
                distance_from_balance = abs(neighbours_preferences[assignment][1].item() + self.cumulative_environmental_impact)
                if assignment == self.assignment:
                    temperature = self.totalIterations - self.iteration
                    metropolis = math.exp(-self.iteration / temperature)
                    test = random.uniform(0, 1)
                    if test < metropolis:
                        distance_from_balance = math.inf
                if distance_from_balance < criterion:
                    criterion = distance_from_balance
                    self.alterValue = assignment
        else:
            self.alterValue = self.assignment

    # PHASE 2 - Credits - from the options that are beneficial to him
    # choose the option that will least distance him from the balance
    def strategy_moral_licensing(self, indications):
        beneficial_to_me = self.beneficial_to_myself(indications)
        if beneficial_to_me:  # not empty
            criterion = math.inf
            for assignment in beneficial_to_me:
                distance_from_balance = abs(beneficial_to_me[assignment][1].item() + self.cumulative_environmental_impact)
                if assignment == self.assignment:
                    temperature = self.totalIterations - self.iteration
                    metropolis = math.exp(-self.iteration / temperature)
                    test = random.uniform(0, 1)
                    if test < metropolis:
                        distance_from_balance = math.inf
                if distance_from_balance < criterion:
                    criterion = distance_from_balance
                    self.alterValue = assignment
        else:
            self.alterValue = self.assignment

    def __str__(self):
        s = "Careful, utility: " + str(round(self.utility)) + ", EI: " + str(self.cumulative_environmental_impact) + \
            ", assignment: " + str(self.assignment)
        return s


# _______________________________________________________________________________________________________________
class GenerousAgent(MoralAgent):

    # PHASE 2 - Debits - from the neighbours’ preferences
    # Choose the option that is most beneficial for the society
    def strategy_moral_compensation(self, indications):
        neighbours_preferences = self.neighbours_preferences(indications)
        if neighbours_preferences:  # not empty
            criterion = -math.inf
            for assignment in neighbours_preferences:
                social_gain = neighbours_preferences[assignment][1].item()
                if social_gain > criterion:
                    criterion = social_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    # PHASE 2 - Credits - from the options that are beneficial to him
    # choose according to neighbours’ preferences
    def strategy_moral_licensing(self, indications):
        beneficial_to_me = self.beneficial_to_myself(indications)
        if beneficial_to_me:  # not empty
            # print(beneficial_to_me)
            criterion = -math.inf
            for assignment in beneficial_to_me:
                social_gain = beneficial_to_me[assignment][1].item()
                if social_gain > criterion:
                    criterion = social_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    def __str__(self):
        s = "Generous, utility: " + str(round(self.utility)) + ", EI: " + str(self.cumulative_environmental_impact) + \
            ", assignment: " + str(self.assignment)
        return s


# _______________________________________________________________________________________________________________
class SelfishAgent(MoralAgent):

    # PHASE 2 - Debits - if all neighbours_preferences bad - choose what best for myself
    def strategy_moral_compensation(self, indications):
        neighbours_preferences = self.neighbours_preferences(indications)
        if neighbours_preferences:  # not empty
            criterion = -math.inf
            for assignment in neighbours_preferences:
                my_gain = neighbours_preferences[assignment][0]
                if my_gain > criterion:
                    criterion = my_gain
                    next_assignment = assignment
            profitability = criterion - (self.totalIterations - self.iteration)
            if profitability > 0:
                self.alterValue = next_assignment
            elif (math.exp(profitability / (self.iteration + 10))) < random.uniform(0, 1):
                self.strategy_moral_licensing(indications)
            else:
                self.alterValue = next_assignment
        else:
            self.strategy_moral_licensing(indications)

    # PHASE 2 - Credits - Choose the option that is most beneficial to him
    def strategy_moral_licensing(self, indications):
        beneficial_to_me = self.beneficial_to_myself(indications)
        if beneficial_to_me:  # not empty
            criterion = -math.inf
            for assignment in beneficial_to_me:
                my_gain = beneficial_to_me[assignment][0]
                if my_gain > criterion:
                    criterion = my_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    def __str__(self):
        s = "Selfish, utility: " + str(round(self.utility)) + ", EI: " + str(self.cumulative_environmental_impact) + \
            ", assignment: " + str(self.assignment)
        return s


# _______________________________________________________________________________________________________________
class RandomAgent(MoralAgent):

    # PHASE 2 - Debits - Choose at random from the options that are beneficial for the society
    def strategy_moral_compensation(self, indications):
        neighbours_preferences = self.neighbours_preferences(indications)
        if neighbours_preferences:  # not empty
            next_assignment = random.choice(list(neighbours_preferences))
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    # PHASE 2 - Credits - Choose at random from the options that are beneficial to him
    def strategy_moral_licensing(self, indications):
        beneficial_to_me = self.beneficial_to_myself(indications)
        if beneficial_to_me:  # not empty
            next_assignment = random.choice(list(beneficial_to_me))
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    def __str__(self):
        s = "Random Agent, utility: " + str(round(self.utility)) + ", EI: " + str(self.cumulative_environmental_impact) + \
            ", assignment: " + str(self.assignment)
        return s


# _______________________________________________________________________________________________________________
class CalculatedAgent(MoralAgent):

    # PHASE 2 - Debits - calculate the weigh:
    # how much the assignment will bring me closer to balance and how much he will “pay” for it,
    # choose the with the highest social benefit and minimum harm to the utility
    def strategy_moral_compensation(self, indications):
        neighbours_preferences = self.neighbours_preferences(indications)
        if neighbours_preferences:  # not empty
            criterion = -math.inf
            for assignment in neighbours_preferences:
                social_gain = neighbours_preferences[assignment][1].item()
                my_gain = neighbours_preferences[assignment][0]
                cumulative_gain = social_gain + my_gain
                if cumulative_gain > criterion:
                    criterion = cumulative_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    # PHASE 2 - Credits - calculate the weigh:
    # how much the assignment will distance it from balance and how much he will gain from it,
    # choose the assignment with the highest benefit and minimum distance.
    def strategy_moral_licensing(self, indications):
        beneficial_to_me = self.beneficial_to_myself(indications)
        if beneficial_to_me:  # not empty
            criterion = -math.inf
            for assignment in beneficial_to_me:
                social_gain = beneficial_to_me[assignment][1].item()
                my_gain = beneficial_to_me[assignment][0]
                cumulative_gain = (0.5-(self.iteration/(2*self.totalIterations)))*social_gain + (0.5+(self.iteration/(2*self.totalIterations)))*my_gain
                if cumulative_gain > criterion:
                    criterion = cumulative_gain
                    next_assignment = assignment
            self.alterValue = next_assignment
        else:
            self.alterValue = self.assignment

    def __str__(self):
        s = "Calculated, utility: " + str(round(self.utility)) + ", EI: " + str(self.cumulative_environmental_impact) +\
            ", assignment: " + str(self.assignment)
        return s
