from .podcast import Podcast


def setup(bot):
    bot.add_cog(Podcast(bot))