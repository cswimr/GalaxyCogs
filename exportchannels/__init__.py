from .exportchannels import ExportChannels

def setup(bot):
    bot.add_cog(ExportChannels(bot))