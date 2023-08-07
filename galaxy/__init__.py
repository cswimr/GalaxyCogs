from .galaxy import Galaxy


async def setup(bot):
    await bot.add_cog(Galaxy(bot))
