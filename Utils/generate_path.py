import json
from math import atan2, radians, cos, sin, asin, sqrt , degrees, acos, pi
import numpy as np

class Path_plan:
    def __init__(self, gcp, save_path, Application_width,turning_radius,tractor_wheelbase):
        """
        :param gcp- gcp pooints of path or boundary
        """
        self.gcp = gcp
        self.savepath=save_path
        self.Application_width=Application_width
        self.turning_radius=turning_radius
        self.tractor_wheelbase=tractor_wheelbase

        
    def path(self):

        #tp= self.path_planning(self.gcp, 2.2,3.4,2.2)
        tp= self.path_planning(self.gcp,self.Application_width,self.turning_radius,self.tractor_wheelbase)
        self.save_path(tp)
        
        return tp

    def save_path_txt(self, data):
        f = open(self.save_path, 'w')
        for item in data:
            f.write(str(item[0])+","+str(item[1])+"\r\n")
        f.close()
        print("path data stored to file in data/path_points.txt")
    
    def save_path(self, path_points):
        data = {
            "farm_boundary": self.gcp,
            "Application_width": self.Application_width,
            "Turning_radius":self.turning_radius,
            "Tractor_wheelbase": self.tractor_wheelbase,
            "path_points":path_points
        }

       
        with open(self.savepath, "w") as file:
            json.dump(data, file, indent=4)

        print("Data saved to ",self.savepath)

    def rotate(self,track):
        
        xyz=[]
        if len(track)>1:
            for i in range(0,len(track)):
                xyz.append(track[(len(track)-1)-i])
         
        return xyz
   
    def haversine(self,lat1,lon1,lat2,lon2):
                     
        try:  
        	# convert decimal degrees to radians 
          lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        	# self.haversine formula 
          dlon = lon2 - lon1 
          dlat = lat2 - lat1 
          a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
          c = 2 * asin(sqrt(a)) 
          r = 6378100 
        
        except:
            pass

        return c * r
        	

	     
    def angle(self,gcp_1,gcp_2):
        delta_L = gcp_2[1] - gcp_1[1]
        X = cos(radians(gcp_2[0])) * sin(radians(delta_L))
        Y = cos(radians(gcp_1[0])) * sin(radians(gcp_2[0])) - sin(radians(gcp_1[0])) * cos(radians(gcp_2[0])) * cos(radians(delta_L))
        beta = degrees(atan2(X,Y))
        if beta >= 0:
            final_bearing = beta
        else:
            final_bearing = 360 + beta
        return final_bearing,beta



    #------------------------------------------------------------------------------------------LOC


    def track(self,gcp_1,gcp_2,scale_div): 
        plot_pt = list()
        plot_pt.append(gcp_1)

        delta_L = gcp_2[1] - gcp_1[1]
        dist = self.haversine(gcp_1[0],gcp_1[1],gcp_2[0],gcp_2[1])
        X = cos(radians(gcp_2[0])) * sin(radians(delta_L))
        Y = cos(radians(gcp_1[0])) * sin(radians(gcp_2[0])) - sin(radians(gcp_1[0])) * cos(radians(gcp_2[0])) * cos(radians(delta_L))
        beta = degrees(atan2(X,Y))

        if beta >= 0:
            final_bearing = beta
        else:
            final_bearing = 360 + beta

        earth_radius = 6378100
        data_div = scale_div
        number_pts = int(round(dist) / data_div)

        for i in range(0,number_pts):
            angular_dist = data_div/earth_radius
            new_lat = degrees(asin(sin(radians(gcp_1[0])) * cos(angular_dist) + cos(radians(gcp_1[0]))*sin(angular_dist)*cos(radians(beta))))
            new_long = gcp_1[1] + degrees(atan2(sin(radians(beta))*sin(angular_dist)*cos(radians(gcp_1[0])),cos(angular_dist)-sin(radians(gcp_1[0]))*sin(radians(new_lat))))
            plot_pt.append([new_lat,new_long]) 
            data_div = data_div + scale_div
        plot_pt.append(gcp_2)
        return plot_pt,dist,final_bearing

        
    def center_circle(self,gcp_1, gcp_2, beta, radius, width,alpha):
        plot_pt=[]
        plot_pt2=[]
        center=[]
        center1=[]
        dist=radius
        
        if beta>=0:
            final_bearing = (beta+180)
            beta1=beta
        else:
            mid_angle=360+beta
            final_bearing = mid_angle+180
            beta1=360+beta
            
        earth_radius = 6378100

        angular_dist = dist/earth_radius
        
        new_lat = degrees(asin(sin(radians(gcp_1[0])) * cos(angular_dist) + cos(radians(gcp_1[0]))*sin(angular_dist)*cos(radians(final_bearing))))
        new_long = gcp_1[1] + degrees(atan2(sin(radians(final_bearing))*sin(angular_dist)*cos(radians(gcp_1[0])),cos(angular_dist)-sin(radians(gcp_1[0]))*sin(radians(new_lat))))
       
        plot_pt.append([new_lat, new_long])

     
        
        new_lat2 = degrees(asin(sin(radians(gcp_2[0])) * cos(angular_dist) + cos(radians(gcp_2[0]))*sin(angular_dist)*cos(radians(beta1))))
        new_long2 = gcp_2[1] + degrees(atan2(sin(radians(beta1))*sin(angular_dist)*cos(radians(gcp_2[0])),cos(angular_dist)-sin(radians(gcp_2[0]))*sin(radians(new_lat2))))
        
        plot_pt2.append([new_lat2, new_long2])
        
        
        return plot_pt, plot_pt2
        
    def arcfirst(self,new_center, final_bearing, radius):
        plot_pt=[]
        dist=radius
        
        earth_radius=6378100
        angular_dist=dist/earth_radius
        
        A_lat=degrees(asin(sin(radians(new_center[0][0])) * cos(angular_dist) + cos(radians(new_center[0][0]))*sin(angular_dist)*cos(radians(final_bearing))))    
        A_long= new_center[0][1] + degrees(atan2(sin(radians(final_bearing))*sin(angular_dist)*cos(radians(new_center[0][0])),cos(angular_dist)-sin(radians(new_center[0][0]))*sin(radians(A_lat))))
        plot_pt.append([A_lat,A_long])
        
        return plot_pt
     
    def distancebet(self,gcp_1,gcp_2):
        
        R=6378100
        delphi=(gcp_1[0]-gcp_2[0])*pi/180
        dellam=(gcp_1[1]-gcp_2[1])*pi/180
        a=sin(delphi/2)**2+cos(gcp_1[0]*pi/180)*cos(gcp_2[0]*pi/180)*sin(dellam/2)**2
        c=2*atan2(sqrt(a),sqrt(1-a))
        d=R*c
        return d   
        
    def flatturn(self,gcp_1,gcp_2, turning_radius):
        turn=[]

        bear,coef = self.angle(gcp_1,gcp_2)
        
        widthoftrack=self.distancebet(gcp_1,gcp_2)
        dist = turning_radius

        alpha=90
        
        new_center, new_center2=self.center_circle(gcp_1,gcp_2, bear+180,dist,2.8,alpha)
        
        a=np.linspace(0,alpha,1)
        
        for i in range(0,len(a)):           
            newgcp2=self.arcfirst(new_center, bear+(90-a[i]), dist)
            
       
        for i in reversed(range(0,len(a))):       
            newgcp=self.arcfirst(new_center2,bear+90+a[i], dist)      
            
        
        dist_pts = self.distancebet(newgcp2[len(newgcp2)-1],newgcp[len(newgcp)-1])
        

        turn.append(newgcp2[len(newgcp2)-1])     
        turn.append(newgcp[len(newgcp)-1])
        
        #print(len(turn))

        return turn
    
    def turn(self,gcp_1,gcp_2, turning_radius):
        turn=[]
        bear,coef = self.angle(gcp_1,gcp_2)

        widthoftrack=self.distancebet(gcp_1,gcp_2)
        dist = turning_radius
        w=widthoftrack
        q=(2*dist+w)/(4*dist)
        try:
            al=acos(q)
            alpha=al*(180/pi)
            
            new_center, new_center2=self.center_circle(gcp_1,gcp_2, bear,dist,2.8,alpha)
            centerofcircle=self.arcfirst(new_center,bear+alpha,dist*2)

            a=np.linspace(0,alpha,2)
            a=a[1:]
            
            for i in range(0,len(a)): 
    
                newgcp=self.arcfirst(new_center,bear+a[i], dist)      
                turn.append(newgcp[len(newgcp)-1])
                
            angle1=bear-alpha
            angle2=alpha+bear
            angle3=180+(alpha+bear)            
               
            h=np.linspace(angle1,angle3,5)
            h=[h[1],h[3]]

            for i in reversed(range(0,len(h))):
                circle=self.arcfirst(centerofcircle, h[i],dist)
                turn.append(circle[len(newgcp)-1]) 

            for i in reversed(range(0,len(a))):                           
                newgcp2=self.arcfirst(new_center2, bear+(180-a[i]), dist)
                turn.append(newgcp2[len(newgcp2)-1]) 
            
        except:
            pass


        return turn
             

    def points(self,gcp_1,dist,ang):
        beta=ang
        earth_radius = 6378100
        angular_dist = dist/earth_radius
        new_lat = degrees(asin(sin(radians(gcp_1[0])) * cos(angular_dist) + cos(radians(gcp_1[0]))*sin(angular_dist)*cos(radians(beta))))
        new_long = gcp_1[1] + degrees(atan2(sin(radians(beta))*sin(angular_dist)*cos(radians(gcp_1[0])),cos(angular_dist)-sin(radians(gcp_1[0]))*sin(radians(new_lat))))
        return [new_lat,new_long]  
        
    def midPoint(self,gcp_1,gcp_2):
        m=[]
        m.append(gcp_1)
        gcp_1_rad_lat = gcp_1[0]*(pi/180)
        gcp_1_rad_lon = gcp_1[1]*(pi/180)
        gcp_2_rad_lat = gcp_2[0]*(pi/180)
        gcp_2_rad_lon = gcp_2[1]*(pi/180)
        
        dlon = gcp_2_rad_lon - gcp_1_rad_lon
        Bx = cos(gcp_2_rad_lat)*cos(dlon)
        By = cos(gcp_2_rad_lat)*sin(dlon)
        ym = sin(gcp_1_rad_lat) + sin(gcp_2_rad_lat)
        xm = sqrt((cos(gcp_1_rad_lat)+Bx)*(cos(gcp_1_rad_lat)+Bx)+By*By)
        lat_m = atan2(ym, xm)
        lng_m = gcp_1_rad_lon + atan2(By,cos(gcp_1_rad_lat)+Bx)
        lat_mid = lat_m*(180/pi)
        lng_mid = lng_m*(180/pi)
        m.append([lat_mid,lng_mid])
        m.append(gcp_2)
        return m
        
    def four_skip(self, trakk):
        trak=[]
        print(len(trakk))
        for i in range(0,len(trakk),9):
            try:
                trak.append(trakk[i])
                
            except:
                continue

            try:
                trak.append(trakk[i+5])
              
            except:
                try:
                    trak.append(trakk[i+4])
                    trak.append(trakk[i+1])
                    trak.append(trakk[i+3])
                    trak.append(trakk[i+2]) 
         
                except:
                    try:
                        trak.append(trakk[i+3]) 
                        
                    except:
                        try:
                            trak.append(trakk[i+2])
                            
                            trak.append(trakk[i+1])
                            
                        except:
                            try:
                                trak.append(trakk[i+1])
                               
                            except:
                                continue
                            continue
                        continue

                    try:
                        trak.append(trakk[i+1])     
                                    
                    except:                        
                        continue
                    try:
                        trak.append(trakk[i+2])   
                       
                    except:     
                        continue
                    continue
                continue
                
            try:
                trak.append(trakk[i+1])
               
            except:
                continue
                
            try:
                trak.append(trakk[i+6])
              
            except:
                try:
                    trak.append(trakk[i+4])   
                    trak.append(trakk[i+2])
                    trak.append(trakk[i+3])
                 
                    continue 
                except:
                    continue
            
            try:
                trak.append(trakk[i+2])
               
            except:
                continue
            
            try:
                trak.append(trakk[i+7])
                
            except:
                trak.append(trakk[i+4])
                trak.append(trakk[i+3])
              
                continue
            
            try:
                trak.append(trakk[i+3])
         
            except:
                continue
            
            try:
                trak.append(trakk[i+8])

            except:
                trak.append(trakk[i+4])
                continue
            try:
                trak.append(trakk[i+4])

            except: 
                continue
        return trak
    def path_planning(self,gcp,Application_width,turning_radius,tractor_wheelbase):
        final_track=[]
        filt_side=[]
        sides=[]
        sides_k=[]
        trak=[]
        green=[]
        inf_data={}
        blue=[]
        trakk=[]
        defa=[]
        #turnss=1 : uturn, turnss=2 : omega turn, turnss=3 : flat turn
        turnss=3
        
        for lo in range(0,len(gcp)):
            gcp_1 = gcp[lo][0]
            gcp_2 = gcp[lo][1]
            dist_data = self.haversine(gcp_1[0],gcp_1[1],gcp_2[0],gcp_2[1])
            inf_data[((gcp_1[0],gcp_1[1]),(gcp_2[0],gcp_2[1]))]=(dist_data)
      
            
        coord = (max(inf_data, key=inf_data.get))
        lis=list(coord[0])
        coor=[]
        coor.append(lis)
        lis=list(coord[1])
        coor.append(lis)

        coord_dist = self.haversine(coord[0][0],coord[0][1],coord[1][0],coord[1][1])
        long_pts,long_dist,long_bearing = self.track(coord[0],coord[1],1)
        print(long_dist,long_bearing)
        angle_val = self.angle(coord[0],coord[1])

        dis=Application_width/2+0.5;
        point=[]

        m=gcp.index(coor)
        inf_data.clear()
        gcpp=[]
        gcpp=(gcp[m:len(gcp)]).copy()
        gcpp.extend(gcp[:m])
        
       
        for lo in range(0,len(gcpp)):
            gcp_1 = gcpp[lo][0]
            gcp_2 = gcpp[lo][1]
            dist_data = self.haversine(gcp_1[0],gcp_1[1],gcp_2[0],gcp_2[1])
            inf_data[((gcp_1[0],gcp_1[1]),(gcp_2[0],gcp_2[1]))]=(dist_data)

        for n in inf_data:
            if n == coord:
                
                continue

            theta, th=self.angle(n[0],n[1])
            delta=abs(long_bearing-theta)
            delta=min(delta,360-delta)

            diss=dis/sin(radians(delta))
            angular_dist=diss/6378100
        
            A_lat=degrees(asin(sin(radians(n[0][0])) * cos(angular_dist) + cos(radians(n[0][0]))*sin(angular_dist)*cos(radians(theta))))    
            A_long= n[0][1] + degrees(atan2(sin(radians(theta))*sin(angular_dist)*cos(radians(n[0][0])),cos(angular_dist)-sin(radians(n[0][0]))*sin(radians(A_lat))))
            point.append([A_lat,A_long])
            
            
            p=abs(Application_width/sin(radians(delta)))
            pok,nok,gok = self.track([point[0][0],point[0][1]],n[1],p)
            po,no,go = self.track(n[0],n[1],0.1)

            d=self.haversine(pok[len(pok)-1][0],pok[len(pok)-1][1],pok[len(pok)-2][0],pok[len(pok)-2][1])
            
            
            for k in range(0,len(pok)):
                try:
                    if d<p and p>1: 
                        pok.pop()
                        dis=Application_width-d*abs(sin(radians(delta)))
                        
                        d=self.haversine(pok[len(pok)-1][0],pok[len(pok)-1][1],pok[len(pok)-2][0],pok[len(pok)-2][1])
                    else:
                        break
                except:
                    pass

            green.append(pok)
            blue.append(po)
            point.clear()

        for k in blue:
            for h in k:
                sides.append(h)
                   
        for k in green:
            for h in k:
                sides_k.append(h)    
      
        z_in=[]
        defa =[]         
        
        for i in range(0,len(sides_k)):
            z_in=[]
            for k in range(0,len(sides)):
                z_out = sides[k]
                sh,sh_dis = self.angle(z_out,sides_k[i])
                
                if int(sh) == int(long_bearing):
                
                    dt = [z_out,sides_k[i]]
                       
                    z_in.append(dt)
                        
                    if len(z_in) > 1:
                        filt_side.append(z_in[0])
                    else:
                        filt_side.append(dt)
        defa =[]
        for x in filt_side:
            if x not in defa:
                defa.append(x)
                
        trakk=[]
        
        

        for pi in range(0,len(defa)):
            track_dist = self.haversine(defa[pi][0][0],defa[pi][0][1],defa[pi][1][0],defa[pi][1][1])
            #print(track_dist)
            try:        
                ber,az_r = self.angle(defa[pi][0],defa[pi][1])
                
                if track_dist > 4*(Application_width)+tractor_wheelbase:  
                    if turnss==1 or turnss==3:       
                        x_imp = turning_radius
                    if turnss==2:
                        x_imp=turning_radius*2.5
                    mid_imp = track_dist - 2*x_imp
                    head_a = self.points(defa[pi][0],x_imp,az_r)
                    head_b = self.points(defa[pi][0],mid_imp+x_imp,az_r)
                    middle_pt=self.midPoint(head_a,head_b)
                    if int(self.angle(middle_pt[0],middle_pt[1])[0])==int(long_bearing):
                        
                        trakk.append([head_a,head_b])
                        #dist_Ab = 5
                        #points_added = self.track(head_a,head_b,dist_Ab)
                        #trakk.append(points_added[0])

            except IndexError:
                pi=pi+1
                    

        
        #4skip
        trak=self.four_skip(trakk)
        
                   
        for i in range(0, len(trak)):
              
            
            try:
                if i%9==0 or i%9==2 or i%9==4 or i%9==6 or i%9==8:
                    
                    if i%2==0: 
                        final_track.append(self.rotate(trak[i]))    
                        final_track.append(self.flatturn(trak[i][0],trak[i+1][0],turning_radius))       
                    if i%2==1:
                        final_track.append((trak[i])) 
                        final_track.append(self.rotate(self.flatturn(trak[i+1][len(trak[i+1])-1],trak[i][len(trak[i])-1],turning_radius)))

                if i%9==1 or i%9==3 or i%9==5 or i%9==7:
                    
                    if i%2==0: 
                        final_track.append(self.rotate(trak[i]))         
                        final_track.append(self.rotate(self.flatturn(trak[i+1][0],trak[i][0],turning_radius)))        
                    if i%2==1:
                        final_track.append(trak[i]) 
                        final_track.append((self.flatturn(trak[i][len(trak[i])-1],trak[i+1][len(trak[i+1])-1],turning_radius)))
                
              
            except IndexError:
                pass
        
        flat_track=[]
        final_track = [ele for ele in final_track if ele != []]
        
        count=0
        for i in range(0, len(final_track)):
            for j in range(0, len(final_track[i])):
                flat_track.append(final_track[i][j])
                #print(str(final_track[i][j][0])+","+str(final_track[i][j][1]))
       
        return (flat_track)
            
