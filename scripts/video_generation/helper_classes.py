import numpy as np


class InstanceDB:
    _instances = None
    _instanceid_cnt = 0

    def __init__(self, instances=None):
        self._instances = [] if instances is None else instances

    def __getitem__(self, item):
        return self.get_instance_by_id(item)
        # return self._instances[item]

    def __len__(self):
        return len(self._instances)

    def __repr__(self):
        return self._instances.__str__()

    def append(self, item):
        return self._instances.append(item)

    def append_frame_to_instance(self, instance_id, new_frame_data, instance_of=None):
        # creates a new instance if instance does not yet exist
        #print("appending frame "+repr(new_InstanceFrameData)+" to instanceid="+str(instance_id))
        found = False
        for instance in self._instances:
            if instance.instance_id == instance_id:
                instance.frames.append(new_frame_data)
                found = True
        if not found:
            if instance_of is not None:
                self._instances.append(
                    Instance(instance_id, instance_of, new_frame_data))
            else:
                raise ValueError(
                    "you need to pass a label (instance_of) to create new instances")

    def get_instance_ids_in_frame(self, frame_nr):
        ids = []
        for instance in self._instances:
            for frame in instance.frames:
                if frame.frame_nr == frame_nr:
                    ids.append(instance.instance_id)
        return ids

    def get_instances_in_frame(self, frame_nr):
        insts = []
        for instance in self._instances:
            for frame in instance.frames:
                if frame.frame_nr == frame_nr:
                    insts.append(instance)
        return insts

    def get_instances_of_type_in_frame(self, instance_of, frame_nr):
        insts = []
        for instance in self._instances:
            if instance.instance_of == instance_of:
                for frame in instance.frames:
                    if frame.frame_nr == frame_nr:
                        insts.append(instance)
        return insts

    def get_instance_by_id(self, instance_id):
        for instance in self._instances:
            if instance.instance_id == instance_id:
                return instance

    def get_unused_instance_id(self):
        self._instanceid_cnt += 1
        return self._instanceid_cnt

    def clean(self, frame_nr):
        # returns all instances that do not occur in the frame frame_nr and deletes them from the instances list
        keep_ids = self.get_instance_ids_in_frame(frame_nr)
        delete_instances = [
            instance for instance in self._instances if instance.instance_id not in keep_ids]
        self._instances[:] = [
            instance for instance in self._instances if instance.instance_id in keep_ids]
        return delete_instances


class Instance:
    instance_id = None
    instance_of = None  # label (string)
    frames = None  # List of FrameData

    def __init__(self, instance_id, instance_of, first_FrameData):
        self.instance_id = instance_id
        self.instance_of = instance_of
        self.frames = list([first_FrameData])

    def __repr__(self):
        return ("{'i_id':"+str(self.instance_id) +
                ",i_of:'"+self.instance_of+"',frames:"+self.frames.__str__()+"}")

    def get_frame_with_nr(self, frame_nr):
        for frame in self.frames:
            if frame.frame_nr == frame_nr:
                return frame
        raise IndexError("could not find a frame with nr=" +
                         frame_nr+" in instance"+repr(self))


class InstanceFrameData:
    frame_nr = None
    segm_mask = None
    segm_bbox = None
    segm_rbox = None

    def __init__(self, frame_nr, segm_mask, segm_bbox, segm_rbox):
        self.frame_nr = frame_nr
        self.segm_mask = segm_mask
        self.segm_bbox = segm_bbox
        self.segm_rbox = segm_rbox

    def __repr__(self):
        return ("'"+str(self.frame_nr) +
                ("T" if self.segm_mask is not None else "F") +
                ("T" if self.segm_bbox is not None else "F") +
                ("T" if self.segm_rbox is not None else "F") + "'")

    def __str__(self):
        return ("{'fr':"+str(self.frame_nr) +
                ",'sm':"+str(list(self.segm_mask.shape) if self.segm_mask is not None else None) +
                ",'sb':"+str(list(np.array(self.segm_bbox).shape) if self.segm_bbox is not None else None) +
                ",'sr':"+str(list(np.array(self.segm_rbox).shape) if self.segm_rbox is not None else None)+"}")


class Tube:
    label = None
    tube_id = None

    min_x = float("inf")
    min_y = float("inf")
    max_x = 0
    max_y = 0
    min_frame = float("inf")
    max_frame = 0


    def __init__(self, instance):
        self.create_from_instance(instance)

    def create_from_instance(self, instance):
        for frame in instance.frames:
            self.min_frame = frame.frame_nr if frame.frame_nr < self.min_frame else self.min_frame
            self.max_frame = frame.frame_nr if frame.frame_nr > self.max_frame else self.max_frame
            for point in frame.segm_bbox:
                self.min_x = point[0] if point[0] < self.min_x else self.min_x
                self.min_y = point[1] if point[1] < self.min_y else self.min_y
                self.max_x = point[0] if point[0] > self.max_x else self.max_x
                self.max_y = point[1] if point[1] > self.max_y else self.max_y
        self.label = instance.instance_of
        self.tube_id = instance.instance_id

    def __repr__(self):
        return ("{'type':'"+self.label+"','iid':"+str(self.tube_id)+",'dim':'"+
                str([self.min_x, self.min_y, self.max_x, self.max_y, self.min_frame, self.max_frame])+"'}")
