from .podcast import Podcast


async def setup(bot):
    await bot.add_cog(Podcast(bot))
