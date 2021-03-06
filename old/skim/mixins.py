# ---> python imports
import math
# ---> rootpy imports
from rootpy.vector import LorentzVector
from rootpy.extern.hep import pdg
# --> local imports
from decorators import cached_property

dphi = lambda phi1, phi2 : abs(math.fmod((math.fmod(phi1, 2*math.pi) - math.fmod(phi2, 2*math.pi)) + 3*math.pi, 2*math.pi) - math.pi)
dR = lambda eta1, phi1, eta2, phi2: math.sqrt((eta1 - eta2)**2 + dphi(phi1, phi2)**2)


"""
This module contains 'mixin' classes for adding
functionality to Tree objects ('decorating' them).
"""

__all__ = [
    'TrueTau',
    'Tau',
    'EF_Tau',
    'L2_Tau',
    'L1_Tau',
    'TauCategories',
    ]



class MatchedObject(object):

    def __init__(self):
        self.matched = False
        self.matched_dR = 9999.
        self.matched_collision = False
        self.matched_object = None

    def matches(self, other, thresh=.4):
        return self.dr(other) < thresh

    def dr(self, other):
        return dR(self.eta, self.phi, other.eta, other.phi)

    def dr_vect(self, other):
        return dR(self.eta, self.phi, other.Eta(), other.Phi())

    def angle_vect(self, other):
        return self.fourvect.Angle(other)

    def matches_vect(self, vect, thresh=.2):
        return self.dr_vect(vect) < thresh

    def RoIWord_matches(self, other ):
        return self.RoIWord == other.RoIWord

class FourMomentum(MatchedObject):

    def __init__(self):
        super(FourMomentum, self).__init__()

    @cached_property
    def fourvect(self):
        vect = LorentzVector()
        vect.SetPtEtaPhiM(self.pt, self.eta, self.phi, self.m)
        return vect

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s (m: %.3f MeV, pt: %.1f MeV, eta: %.2f, phi: %.2f)" % \
            (self.__class__.__name__,self.m,self.pt,self.eta,self.phi)

class ClusterBasedFourMomentum(MatchedObject):

    def __init__(self):
        super(ClusterBasedFourMomentum,self).__init__()

    @cached_property
    def fourvect_clbased(self):
        vect = LorentzVector()
        tau_numTrack = self.numTrack
        tau_nPi0s = self.pi0_n
        if tau_nPi0s==0:
            if self.track_n>0:
                sumTrk = LorentzVector()
                for trk_ind in xrange(0,self.track_n):
                    curTrk = LorentzVector()
                    curTrk.SetPtEtaPhiM(self.track_atTJVA_pt [trk_ind],
                                        self.track_atTJVA_eta[trk_ind],
                                        self.track_atTJVA_phi[trk_ind],
                                         139.8)
                    sumTrk += curTrk
                vect.SetPtEtaPhiM(sumTrk.Pt(), sumTrk.Eta(), sumTrk.Phi(), sumTrk.M())
            else:
                vect.SetPtEtaPhiM(self.pt, self.eta, self.phi, self.m)
        elif tau_nPi0s==1 or tau_nPi0s==2:
            if self.pi0_vistau_pt==0:
                vect.SetPtEtaPhiM(self.pt, self.eta, self.phi, self.m)
            else:
                vect.SetPtEtaPhiM(self.pi0_vistau_pt, self.pi0_vistau_eta,
                                  self.pi0_vistau_phi, self.pi0_vistau_m )
        else:
            vect.SetPtEtaPhiM (self.pi0_vistau_pt, self.pi0_vistau_eta,
                                self.pi0_vistau_phi, self.pi0_vistau_m)
        return vect
    
class Tau(FourMomentum,ClusterBasedFourMomentum):

    def __init__(self):
        super(FourMomentum, self).__init__()
        super(ClusterBasedFourMomentum, self).__init__()
        self.index_matched_truth = -1
        self.index_matched_EF    = -1
        self.dR_matched_EF       = -1111
        self.index_matched_L1    = -1
        self.dR_matched_L1       = -1111

class EF_Tau(FourMomentum):

    def __init__(self):
        self.m = 0.
        super(FourMomentum, self).__init__()
        self.index_matched_L2 = -1
        self.index_matched_L1 = -1

class L2_Tau(FourMomentum):

    def __init__(self):
        self.m = 0.
        super(FourMomentum, self).__init__()
        self.index_matched_L1 = -1

class L1_Tau(FourMomentum):

    def __init__(self):
        self.m = 0.
        self.pt = self.tauClus
        super(FourMomentum, self).__init__()


class TrueTau(FourMomentum):

    def __init__(self):
        super(FourMomentum, self).__init__()
        self.fourvect_vis = self.getTruthVis4Vector()
        #  self.ChargedPions, self.NeutralPions = self.getTruthDecays()
    #-----------------------------------------------------------
    def getTruthVis4Vector(self):
        """Get the LorentzVector for the visible truth tau """
        vector = LorentzVector()
        vector.SetPtEtaPhiM(self.vis_Et,self.vis_eta,self.vis_phi,self.vis_m)
        return vector

    #-----------------------------------------------------------
#     def getTruthDecay(self):
#         """Get 4-vectors for the true charged pions"""
#         productsIndex = self.truthAssoc_index

#         ChargedPions = []
#         NeutralPions = []

#         for i in range(0, len(productsIndex)):
#             k = productsIndex[i]
#             PDGID  = mc_parts[k].pdgId
#             status = mc_parts[k].status

#             if abs(PDGID) == 15 and status == 2:
#                 indices = self.getDaughters(k)

#                 # Loop over tau final daughters to find charged pions and pi0s
#                 for j in indices:
#                     pdgId  = mc_parts[j].pdgId

#                     if abs(pdgId) == 211 or abs(pdgId) == 321:
#                         pt  = mc_parts[j].pt
#                         eta = mc_parts[j].eta
#                         phi = mc_parts[j].phi
#                         m   = mc_parts[j].m
#                         PiCh = LorentzVector()
#                         PiCh.SetPtEtaPhiM(pt, eta, phi, m)
#                         ChargedPions.append(PiCh)

#                     if abs(pdgId) == 111:
#                         photons = self.getPhotons(j)
#                         photonVectors = []
#                         for p in photons:
#                             pt  = mc_parts[p].pt
#                             eta = mc_parts[p].eta
#                             phi = mc_parts[p].phi
#                             m   = mc_parts[p].m

#                             ph = LorentzVector()
#                             ph.SetPtEtaPhiM(pt, eta, phi, m)
#                             photonVectors.append(ph)

#                         NeutralPions.append(photonVectors)
        
#         return ChargedPions, NeutralPions


#     #-----------------------------------------------------------
#     def getDaughters(self, parentIndex):
#         """To be used recursively until all particles are in final state"""
#         # Get daughters:
#         daughters = mc_parts[parentIndex].child_index
#         daughtersData = []

#         for i in range(0, len(daughters)):
#             k = daughters[i]
#             status = mc_parts[k].status
#             pdgId  = mc_parts[k].pdgId

#             if status == 1:
#                 daughtersData.append(k)

#             if status == 2:
#                 if pdgId == 111:
#                     daughtersData.append(k)
#                 else:
#                     newDaughtersData = self.getDaughters(k)
#                     daughtersData.extend(newDaughtersData)

#         return daughtersData
            

#     #-----------------------------------------------------------
#     def getPhotons(self, parentIndex):
#         """Get the photon daughters of a pi0"""
#         daughters = mc_parts[parentIndex].child
#         return list(daughters)

