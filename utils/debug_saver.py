from config import OUT_DIR, OUT_EXT, SAVE

from matplotlib import pyplot as plt, rc


class DebugSaver(object):
    def __init__(self, title: str):
        self.title_ = title
        self.counter_ = 0

    def next_filename_(self) -> str:
        filename = f"{OUT_DIR}/{self.title_}"\
                   f"-{self.counter_:02}.{OUT_EXT}"
        self.counter_ += 1
        return filename

    def save(self):
        if SAVE:
            plt.savefig(self.next_filename_())
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def setup():
        if SAVE:
            rc('xtick', bottom=False, labelbottom=False)
            rc('ytick', left=False, labelleft=False)
            rc('figure.subplot', wspace=0, left=0, right=1,
               hspace=0, top=1, bottom=0)
