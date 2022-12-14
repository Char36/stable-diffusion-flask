import sys

from app import imagine_service_pb2_grpc
from optimizedSD.arguments import Arguments
from optimizedSD.optimized_txt2img import StableDiffusionTxt2Img
from imagine_service_pb2_grpc import imagine__service__pb2
import logging
from concurrent import futures
import grpc

models_path = 'models/ldm/stable-diffusion-v1/'
model = StableDiffusionTxt2Img()

generating = False
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def map_arguments(request):
    arguments = Arguments()

    arguments.prompt = request.data.prompt
    arguments.ddim_steps = request.data.ddim_steps
    arguments.n_iter = request.data.n_iter
    arguments.H = request.data.H
    arguments.W = request.data.W
    arguments.C = request.data.C
    arguments.f = request.data.f
    arguments.n_samples = request.data.n_samples
    arguments.n_rows = request.data.n_rows
    arguments.seed = request.data.seed
    arguments.turbo = request.data.turbo
    arguments.scale = request.data.scale

    return arguments


def build_response(result):
    """
    """

    imagine_response = imagine__service__pb2.ImagineResponse()

    for image in result:
        image_data = imagine__service__pb2.ImageData()
        image_data.seed = str(image['seed'])
        image_data.chunk_data = image['data']
        imagine_response.image_data.append(image_data)

    return imagine_response


class StableDiffusion(imagine_service_pb2_grpc.StableDiffusionServiceServicer):

    def TextToImage(self,
                    request,
                    context):
        """
         Route for generating and returning `n` image results,
         where `n` :== `args.n_samples`

         Serialized as an array of B64-encoded byte arrays.
        """

        global generating
        global model

        if generating:
            raise Exception('text-to-image operation is already running')

        assert hasattr(request, 'data')

        args = map_arguments(request)

        generating = True
        try:
            result = model.imagine(args, image_format='binary')
        finally:
            generating = False

        return build_response(result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    imagine_service_pb2_grpc.add_StableDiffusionServiceServicer_to_server(
        StableDiffusion(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('server started')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
