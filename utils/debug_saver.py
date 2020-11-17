from config import OUT_DIR, OUT_EXT, SAVE

from os import listdir, path, remove
from matplotlib import rc
from matplotlib.pyplot import savefig, show, clf, \
    title as plt_title


class DebugSaver(object):
    instance_counter_ = 0

    def __init__(self, title: str):
        self.title_ = title
        self.counter_ = 0
        self.num_ = DebugSaver.instance_counter_
        DebugSaver.instance_counter_ += 1

    def next_filename_(self, name: str) -> str:
        filename = f"{OUT_DIR}/"\
            f"output{self.num_:02}({self.title_})"\
            f"-source{self.counter_:02}({name}).{OUT_EXT}"
        self.counter_ += 1
        return filename

    def save(self, name: str):
        if SAVE:
            savefig(self.next_filename_(name))
        else:
            plt_title(f"{name} - {self.title_}")
            show()
        clf()

    @staticmethod
    def setup():
        if SAVE:
            rc('xtick', bottom=False, labelbottom=False)
            rc('ytick', left=False, labelleft=False)
            rc('figure.subplot', wspace=0, left=0, right=1,
               hspace=0, top=1, bottom=0)

            folder = OUT_DIR
            for filename in listdir(folder):
                file_path = path.join(folder, filename)
                try:
                    remove(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        # else:
