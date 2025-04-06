import network
import comparisons_functions

num_of_rows = int(4) #3m to szerokość tunelu, 0.7m to szerokość jednej komórki
num_of_columns = int(25)
net = network.network(num_of_rows,num_of_columns) #stworzenie sieci
#dodanie wyjść na obu krawędziach
for i in range(num_of_rows):
    net.add_exit(i,0,False)
    net.add_exit(i,num_of_columns-1,True)

#parametry do symulacji
num_of_agents = 200
p0,p1,p2,p3,p4,p5 = 0.05,0.1,0.2,0.35,0.2,0.1 

N=100 #dla 100 wykonuje sie ok. 3min 15sek
lam_vec=[3, 6, 9, 12]

comparisons_functions.do_staff(density=True, lam_vec=lam_vec, N=N, 
                        num_of_rows=num_of_rows, num_of_columns=num_of_columns, num_of_agents=num_of_agents, p0=p0, p1=p1, p2=p2, p3=p3, p4=p4, p5=p5, net=net)




