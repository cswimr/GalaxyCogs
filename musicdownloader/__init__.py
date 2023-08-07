from .musicdownloader import MusicDownloader


async def setup(bot):
    await bot.add_cog(MusicDownloader(bot))
