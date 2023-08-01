from .musicdownloader import MusicDownloader


def setup(bot):
    bot.add_cog(MusicDownloader(bot))
